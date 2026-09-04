from __future__ import annotations

import argparse
import json
import mimetypes
import os
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock, Thread
from urllib.parse import unquote, urlsplit

import httpx2
from pydantic import ValidationError

from domain_intelligence.io_json import load_input
from domain_intelligence.local_builder import (
    ProviderConfig,
    SeedBuilderError,
    add_source_to_input,
    build_local_input_run,
    build_local_run,
)
from domain_intelligence.models import BootstrapInput

MAX_REQUEST_BYTES = 16_384
JOB_STATUS_FILE = "job-status.json"
SAFE_ID = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
JSONScalar = str | int | float | bool | None
JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


class LocalRequestError(ValueError):
    pass


class LocalAppState:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.demo_root = self.root / "demo"
        self.runs_root = self.root / ".private-intelligence" / "local-runs"
        self.runs_root.mkdir(parents=True, exist_ok=True)
        self._provider = ProviderConfig(
            endpoint=os.environ.get("PRIVATE_INTELLIGENCE_AI_BASE_URL", "").strip(),
            api_key=os.environ.get("PRIVATE_INTELLIGENCE_AI_API_KEY", ""),
            model=os.environ.get("PRIVATE_INTELLIGENCE_AI_MODEL", "").strip(),
        )
        self._jobs: dict[str, dict[str, str | int | None]] = {}
        self._lock = Lock()

    def provider(self) -> ProviderConfig:
        with self._lock:
            return self._provider

    def set_provider(self, provider: ProviderConfig) -> None:
        with self._lock:
            self._provider = provider

    def provider_configured(self) -> bool:
        provider = self.provider()
        return bool(_provider_endpoint(provider.endpoint) and provider.model)

    def _persist_job(self, job: dict[str, str | int | None]) -> None:
        status_path = self.runs_root / str(job["id"]) / JOB_STATUS_FILE
        temporary_path = status_path.with_name(f".{JOB_STATUS_FILE}.{secrets.token_hex(4)}.tmp")
        temporary_path.write_text(
            json.dumps(job, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        temporary_path.replace(status_path)

    def create_job(self, domain: str) -> str:
        job_id = secrets.token_hex(8)
        (self.runs_root / job_id).mkdir(parents=True, exist_ok=False)
        job = {
            "id": job_id,
            "domain": domain,
            "status": "queued",
            "phase": "queued",
            "message": "已排队，准备建立领域底图",
            "percent": 0,
            "error": None,
        }
        with self._lock:
            self._jobs[job_id] = job
        self._persist_job(job)
        return job_id

    def update_job(self, job_id: str, **updates: str | int | None) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            job.update(updates)
            snapshot = dict(job)
        self._persist_job(snapshot)

    def job(self, job_id: str) -> dict[str, str | int | None] | None:
        with self._lock:
            current = self._jobs.get(job_id)
            return dict(current) if current is not None else None

    def jobs(self) -> list[dict[str, str | int | None]]:
        with self._lock:
            jobs = {job_id: dict(job) for job_id, job in self._jobs.items()}
        for run_dir in self.runs_root.iterdir():
            if not run_dir.is_dir() or run_dir.name in jobs:
                continue
            snapshot = _job_snapshot(self, run_dir.name)
            if snapshot is not None:
                jobs[run_dir.name] = snapshot
        return list(jobs.values())


def _is_safe_id(value: str) -> bool:
    return (
        bool(value)
        and len(value) <= 128
        and value[0].isalnum()
        and all(char in SAFE_ID for char in value)
    )


def _provider_endpoint(value: str) -> bool:
    parsed = urlsplit(value)
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
        and not parsed.username
        and not parsed.password
    )


def _safe_artifact_path(state: LocalAppState, job_id: str, relative: str) -> Path | None:
    if not _is_safe_id(job_id) or not relative or relative.startswith("/"):
        return None
    runs_root = state.runs_root.resolve()
    root = (state.runs_root / job_id).resolve()
    try:
        root.relative_to(runs_root)
    except ValueError:
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _safe_demo_path(state: LocalAppState, relative: str) -> Path | None:
    if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        return None
    demo_root = state.demo_root.resolve()
    candidate = (state.demo_root / relative).resolve()
    try:
        candidate.relative_to(demo_root)
    except ValueError:
        return None
    return candidate


def _job_snapshot(state: LocalAppState, job_id: str) -> dict[str, str | int | None] | None:
    current = state.job(job_id)
    if current is not None:
        return current
    if not _is_safe_id(job_id):
        return None
    manifest_path = _safe_artifact_path(state, job_id, "run-manifest.json")
    if manifest_path is not None and manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(manifest, dict):
            return None
        return {
            "id": job_id,
            "domain": str(manifest.get("domain", "")),
            "status": "complete",
            "phase": "complete",
            "message": "领域情报所已经建立，可以打开运行工作台",
            "percent": 100,
            "error": None,
        }
    status_path = _safe_artifact_path(state, job_id, JOB_STATUS_FILE)
    if status_path is None or not status_path.is_file():
        return None
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or payload.get("id") != job_id:
        return None
    status = payload.get("status")
    if status not in {"queued", "running", "failed"}:
        return None
    return {
        "id": job_id,
        "domain": str(payload.get("domain", "")),
        "status": status,
        "phase": str(payload.get("phase", status)),
        "message": str(payload.get("message", "本地运行记录")),
        "percent": payload.get("percent", 0) if isinstance(payload.get("percent", 0), int) else 0,
        "error": str(payload["error"]) if payload.get("error") is not None else None,
    }


def _start_job(
    state: LocalAppState,
    job_id: str,
    domain: str,
    inputs: BootstrapInput | None = None,
) -> None:
    def progress(phase: str, message: str, percent: int) -> None:
        state.update_job(job_id, status="running", phase=phase, message=message, percent=percent)

    def worker() -> None:
        try:
            if inputs is None:
                build_local_run(domain, state.provider(), state.runs_root / job_id, progress)
            else:
                build_local_input_run(
                    inputs,
                    state.runs_root / job_id,
                    progress,
                    input_mode="local_source_addition_live_capture",
                )
        except (
            SeedBuilderError,
            ValidationError,
            httpx2.HTTPError,
            OSError,
            RuntimeError,
            ValueError,
        ) as error:
            state.update_job(
                job_id,
                status="failed",
                phase="failed",
                message="这次运行没有完成",
                error=str(error),
                percent=0,
            )
        else:
            state.update_job(
                job_id,
                status="complete",
                phase="complete",
                message="领域情报所已经建立，可以打开运行工作台",
                percent=100,
            )

    Thread(target=worker, name=f"private-intelligence-{job_id}", daemon=True).start()


def _make_handler(state: LocalAppState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: str) -> None:
            del format, args

        def _send_json(self, status: HTTPStatus, payload: dict[str, JSONValue]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict[str, JSONValue]:
            raw_length = self.headers.get("Content-Length", "")
            try:
                length = int(raw_length)
            except ValueError as error:
                raise LocalRequestError("请求长度无效") from error
            if length < 0 or length > MAX_REQUEST_BYTES:
                raise LocalRequestError("请求内容过大")
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as error:
                raise LocalRequestError("请求不是有效 JSON") from error
            if not isinstance(payload, dict):
                raise LocalRequestError("请求必须是 JSON 对象")
            return payload

        def _send_file(self, path: Path, download: bool = False) -> None:
            try:
                body = path.read_bytes()
            except OSError:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            if content_type.startswith("text/"):
                content_type = f"{content_type}; charset=utf-8"
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            if download:
                self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
            self.end_headers()
            self.wfile.write(body)

        def _local_request_allowed(self) -> bool:
            host = urlsplit(f"//{self.headers.get('Host', '')}").hostname
            if host not in LOCAL_HOSTS:
                return False
            origin = self.headers.get("Origin")
            if not origin:
                return True
            parsed_origin = urlsplit(origin)
            return (
                parsed_origin.scheme in {"http", "https"} and parsed_origin.hostname in LOCAL_HOSTS
            )

        def do_GET(self) -> None:
            parsed = urlsplit(self.path)
            path = unquote(parsed.path)
            if path == "/api/health":
                self._send_json(
                    HTTPStatus.OK,
                    {"status": "ok", "provider_configured": state.provider_configured()},
                )
                return
            if path == "/api/runs":
                jobs = sorted(state.jobs(), key=lambda job: str(job.get("id")), reverse=True)
                self._send_json(HTTPStatus.OK, {"runs": jobs})
                return
            if path.startswith("/api/runs/"):
                parts = path.split("/")
                if len(parts) >= 5 and parts[4] == "artifact":
                    job_id = parts[3]
                    relative = "/".join(parts[5:])
                    artifact = _safe_artifact_path(state, job_id, relative)
                    if artifact is None or not artifact.is_file():
                        self.send_error(HTTPStatus.NOT_FOUND)
                        return
                    self._send_file(artifact, download=artifact.suffix.lower() in {".html", ".htm"})
                    return
                job_id = parts[3] if len(parts) == 4 else ""
                snapshot = _job_snapshot(state, job_id)
                if snapshot is None:
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self._send_json(HTTPStatus.OK, snapshot)
                return
            if path in {"", "/"}:
                asset = _safe_demo_path(state, "local.html")
                if asset is None or not asset.is_file():
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self._send_file(asset)
                return
            if path in {"/local.css", "/local.js"}:
                asset = _safe_demo_path(state, path[1:])
                if asset is None or not asset.is_file():
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self._send_file(asset)
                return
            if path.startswith("/demo/"):
                relative = path.removeprefix("/demo/")
                if not relative:
                    relative = "index.html"
                asset = _safe_demo_path(state, relative)
                if asset is None or not asset.is_file():
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self._send_file(asset)
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            parsed = urlsplit(self.path)
            if not self._local_request_allowed():
                self._send_json(
                    HTTPStatus.FORBIDDEN,
                    {
                        "status": "local_request_only",
                        "message": "私人情报所只接受本机页面发起的写入请求。",
                    },
                )
                return
            try:
                payload = self._read_json()
                if parsed.path == "/api/settings":
                    endpoint = payload.get("endpoint")
                    model = payload.get("model")
                    api_key = payload.get("api_key", "")
                    if (
                        not isinstance(endpoint, str)
                        or len(endpoint) > 500
                        or not _provider_endpoint(endpoint)
                    ):
                        raise LocalRequestError("AI 接口地址无效")
                    if not isinstance(model, str) or not model.strip() or len(model) > 200:
                        raise LocalRequestError("AI 模型名称无效")
                    if not isinstance(api_key, str) or len(api_key) > 1000:
                        raise LocalRequestError("AI 密钥格式无效")
                    state.set_provider(ProviderConfig(endpoint.strip(), api_key, model.strip()))
                    self._send_json(HTTPStatus.OK, {"status": "ok", "provider_configured": True})
                    return
                if parsed.path == "/api/runs":
                    domain = payload.get("domain")
                    if not isinstance(domain, str) or not 1 <= len(domain.strip()) <= 120:
                        raise LocalRequestError("请输入 1 至 120 个字符的领域名称")
                    if not state.provider_configured():
                        self._send_json(
                            HTTPStatus.CONFLICT,
                            {
                                "status": "needs_setup",
                                "message": "请先填写一次 AI 连接信息，密钥只保存在当前运行进程，不会写入项目。",
                            },
                        )
                        return
                    clean_domain = domain.strip()
                    job_id = state.create_job(clean_domain)
                    _start_job(state, job_id, clean_domain)
                    self._send_json(
                        HTTPStatus.ACCEPTED,
                        {"id": job_id, "status": "queued", "message": "已开始建立领域底图"},
                    )
                    return
                parts = parsed.path.split("/")
                if len(parts) == 5 and parts[1:3] == ["api", "runs"] and parts[4] == "sources":
                    job_id = parts[3]
                    snapshot = _job_snapshot(state, job_id)
                    if snapshot is None:
                        self.send_error(HTTPStatus.NOT_FOUND)
                        return
                    if snapshot["status"] != "complete":
                        self._send_json(
                            HTTPStatus.CONFLICT,
                            {
                                "status": "run_not_complete",
                                "message": "请等这次领域建立完成后再加入来源。",
                            },
                        )
                        return
                    input_path = _safe_artifact_path(state, job_id, "bootstrap-input.json")
                    if input_path is None or not input_path.is_file():
                        self._send_json(
                            HTTPStatus.CONFLICT,
                            {
                                "status": "run_not_editable",
                                "message": "这次运行没有可编辑的领域底图。",
                            },
                        )
                        return
                    name = payload.get("name")
                    endpoint = payload.get("endpoint")
                    method = payload.get("method", "static_html")
                    role = payload.get("role", "community")
                    if not all(isinstance(value, str) for value in (name, endpoint, method, role)):
                        raise LocalRequestError("来源名称、入口、获取方式和角色格式无效")
                    try:
                        inputs = load_input(input_path)
                        updated_inputs, source = add_source_to_input(
                            inputs,
                            name,
                            endpoint,
                            method,
                            role,
                        )
                    except (OSError, ValidationError, SeedBuilderError, ValueError) as error:
                        raise LocalRequestError(str(error)) from error
                    new_job_id = state.create_job(updated_inputs.profile.domain)
                    _start_job(state, new_job_id, updated_inputs.profile.domain, updated_inputs)
                    self._send_json(
                        HTTPStatus.ACCEPTED,
                        {
                            "id": new_job_id,
                            "source_id": str(source.id),
                            "status": "queued",
                            "message": "已加入这个来源，正在重建一版可回看的领域情报所。",
                        },
                    )
                    return
                self.send_error(HTTPStatus.NOT_FOUND)
            except LocalRequestError as error:
                self._send_json(
                    HTTPStatus.BAD_REQUEST, {"status": "invalid_request", "message": str(error)}
                )

    return Handler


class LocalServer(ThreadingHTTPServer):
    state: LocalAppState


def create_server(root: Path, host: str = "127.0.0.1", port: int = 8787) -> LocalServer:
    if host not in LOCAL_HOSTS:
        raise ValueError("私人情报所仅允许监听本机地址")
    state = LocalAppState(root)
    server = LocalServer((host, port), _make_handler(state))
    server.state = state
    return server


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="private-intelligence", description="启动私人情报所本地网站"
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="项目目录，默认使用当前目录")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=8787, help="监听端口")
    args = parser.parse_args()
    server = create_server(args.root, args.host, args.port)
    address = server.server_address
    print(f"私人情报所已启动：http://{address[0]}:{address[1]}/")
    print("按 Ctrl-C 停止本地网站")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
