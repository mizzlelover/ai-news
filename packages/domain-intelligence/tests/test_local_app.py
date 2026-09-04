from __future__ import annotations

import http.client
import json
from collections.abc import Iterator
from pathlib import Path
from threading import Thread

import pytest

import domain_intelligence.local_app as local_app_module
from domain_intelligence.io_json import load_input, write_json
from domain_intelligence.local_app import (
    LocalAppState,
    LocalServer,
    _job_snapshot,
    _safe_artifact_path,
    _safe_demo_path,
    create_server,
)


@pytest.fixture
def local_server(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[LocalServer]:
    del tmp_path
    monkeypatch.delenv("PRIVATE_INTELLIGENCE_AI_BASE_URL", raising=False)
    monkeypatch.delenv("PRIVATE_INTELLIGENCE_AI_API_KEY", raising=False)
    monkeypatch.delenv("PRIVATE_INTELLIGENCE_AI_MODEL", raising=False)
    root = Path(__file__).resolve().parents[3]
    server = create_server(root, port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    thread.join(timeout=2)
    server.server_close()


def _request(
    server: LocalServer,
    method: str,
    path: str,
    payload: dict[str, str] | None = None,
    extra_headers: dict[str, str] | None = None,
) -> tuple[int, bytes]:
    address = server.server_address
    connection = http.client.HTTPConnection(address[0], address[1], timeout=3)
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    headers.update(extra_headers or {})
    body = json.dumps(payload).encode() if payload is not None else None
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    result = response.status, response.read()
    connection.close()
    return result


def test_local_site_explains_setup_and_refuses_run_without_provider(
    local_server: LocalServer,
) -> None:
    status, body = _request(local_server, "GET", "/")
    assert status == 200
    assert "给我一个领域".encode() in body

    status, body = _request(local_server, "GET", "/api/health")
    assert status == 200
    assert json.loads(body) == {"status": "ok", "provider_configured": False}

    status, body = _request(local_server, "POST", "/api/runs", {"domain": "数字孪生"})
    assert status == 409
    assert json.loads(body)["status"] == "needs_setup"


def test_local_site_accepts_in_memory_provider_settings(local_server: LocalServer) -> None:
    status, body = _request(
        local_server,
        "POST",
        "/api/settings",
        {"endpoint": "http://127.0.0.1:11434/v1", "model": "qwen3:8b", "api_key": ""},
    )
    assert status == 200
    assert json.loads(body)["provider_configured"] is True

    status, body = _request(local_server, "GET", "/api/health")
    assert status == 200
    assert json.loads(body)["provider_configured"] is True


def test_local_server_rejects_non_loopback_host(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="仅允许监听本机地址"):
        create_server(tmp_path, host="0.0.0.0", port=0)


def test_local_write_rejects_non_local_origin(local_server: LocalServer) -> None:
    status, body = _request(
        local_server,
        "POST",
        "/api/settings",
        {"endpoint": "http://127.0.0.1:11434/v1", "model": "test", "api_key": ""},
        {"Origin": "https://evil.example"},
    )

    assert status == 403
    assert json.loads(body)["status"] == "local_request_only"


def test_local_artifact_path_rejects_run_directory_symlink(tmp_path: Path) -> None:
    state = LocalAppState(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("not for serving", encoding="utf-8")
    (state.runs_root / "escape").symlink_to(outside, target_is_directory=True)

    assert _safe_artifact_path(state, "escape", "secret.txt") is None


def test_local_demo_route_rejects_absolute_path_escape(local_server: LocalServer) -> None:
    status, _ = _request(local_server, "GET", "/demo//etc/hosts")

    assert status == 404


def test_local_demo_path_rejects_symlink_escape(tmp_path: Path) -> None:
    state = LocalAppState(tmp_path)
    state.demo_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("not for serving", encoding="utf-8")
    (state.demo_root / "escape-link").symlink_to(outside, target_is_directory=True)

    assert _safe_demo_path(state, "escape-link/secret.txt") is None


def test_local_failed_job_survives_process_restart(tmp_path: Path) -> None:
    state = LocalAppState(tmp_path)
    job_id = state.create_job("数字孪生")
    state.update_job(
        job_id,
        status="failed",
        phase="failed",
        message="这次运行没有完成",
        error="AI 接口请求失败",
        percent=0,
    )

    restarted = LocalAppState(tmp_path)

    assert _job_snapshot(restarted, job_id) == {
        "id": job_id,
        "domain": "数字孪生",
        "status": "failed",
        "phase": "failed",
        "message": "这次运行没有完成",
        "percent": 0,
        "error": "AI 接口请求失败",
    }


def test_local_site_can_add_source_to_completed_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("PRIVATE_INTELLIGENCE_AI_BASE_URL", raising=False)
    monkeypatch.delenv("PRIVATE_INTELLIGENCE_AI_API_KEY", raising=False)
    monkeypatch.delenv("PRIVATE_INTELLIGENCE_AI_MODEL", raising=False)
    state = LocalAppState(tmp_path)
    run_dir = state.runs_root / "existing-run"
    run_dir.mkdir()
    inputs = load_input(Path(__file__).resolve().parents[1] / "examples" / "data-elements.json")
    write_json(inputs, run_dir / "bootstrap-input.json")
    (run_dir / "run-manifest.json").write_text(
        '{"domain":"data-elements"}',
        encoding="utf-8",
    )
    monkeypatch.setattr(local_app_module, "_start_job", lambda *args, **kwargs: None)
    server = create_server(tmp_path, port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _request(
            server,
            "POST",
            "/api/runs/existing-run/sources",
            {
                "name": "IANA 公开入口",
                "endpoint": "https://www.iana.org/domains/example",
                "method": "static_html",
                "role": "community",
            },
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()

    assert status == 202
    payload = json.loads(body)
    assert payload["status"] == "queued"
    assert payload["source_id"].startswith("user-")
