from __future__ import annotations

import http.client
import json
from collections.abc import Iterator
from pathlib import Path
from threading import Thread

import pytest

from domain_intelligence.local_app import (
    LocalAppState,
    LocalServer,
    _safe_artifact_path,
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
) -> tuple[int, bytes]:
    address = server.server_address
    connection = http.client.HTTPConnection(address[0], address[1], timeout=3)
    headers = {"Content-Type": "application/json"} if payload is not None else {}
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


def test_local_artifact_path_rejects_run_directory_symlink(tmp_path: Path) -> None:
    state = LocalAppState(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("not for serving", encoding="utf-8")
    (state.runs_root / "escape").symlink_to(outside, target_is_directory=True)

    assert _safe_artifact_path(state, "escape", "secret.txt") is None
