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

from domain_intelligence.local_builder import ProviderConfig, SeedBuilderError, build_local_run

MAX_REQUEST_BYTES = 16_384
SAFE_ID = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-"
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

    def create_job(self, domain: str) -> str:
        job_id = secrets.token_hex(8)
        with self._lock:
            self._jobs[job_id] = {
                "id": job_id,
                "domain": domain,
                "status": "queued",
                "phase": "queued",
                "message": "已排队，准备建立领域底图",
                "percent": 0,
                "error": None,
            }
        (self.runs_root / job_id).mkdir(parents=True, exist_ok=False)
        return job_id

    def update_job(self, job_id: str, **updates: str | int | None) -> None:
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(updates)

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


def _job_snapshot(state: LocalAppState, job_id: str) -> dict[str, str | int | None] | None:
    current = state.job(job_id)
    if current is not None:
        return current
    manifest_path = state.runs_root / job_id / "run-manifest.json"
    if not _is_safe_id(job_id) or not manifest_path.is_file():
        return None
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


def _start_job(state: LocalAppState, job_id: str, domain: str) -> None:
    def progress(phase: str, message: str, percent: int) -> None:
        state.update_job(job_id, status="running", phase=phase, message=message, percent=percent)

    def worker() -> None:
        try:
            build_local_run(domain, state.provider(), state.runs_root / job_id, progress)
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
                self._send_file(state.demo_root / "local.html")
                return
            if path in {"/local.css", "/local.js"}:
                self._send_file(state.demo_root / path[1:])
                return
            if path.startswith("/demo/"):
                relative = path.removeprefix("/demo/")
                if not relative or ".." in Path(relative).parts:
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self._send_file(state.demo_root / relative)
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            parsed = urlsplit(self.path)
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
                self.send_error(HTTPStatus.NOT_FOUND)
            except LocalRequestError as error:
                self._send_json(
                    HTTPStatus.BAD_REQUEST, {"status": "invalid_request", "message": str(error)}
                )

    return Handler


class LocalServer(ThreadingHTTPServer):
    state: LocalAppState


def create_server(root: Path, host: str = "127.0.0.1", port: int = 8787) -> LocalServer:
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
