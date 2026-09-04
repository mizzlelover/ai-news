from __future__ import annotations

import socket
from collections.abc import Iterator
from contextlib import AbstractAsyncContextManager
from pathlib import Path

import anyio
import httpx2
import pytest
from pydantic import ValidationError

from domain_intelligence.capture import transport
from domain_intelligence.capture.archive import (
    UnsafeCapturePathError,
    UnsafeSourceIdError,
    content_id,
    write_capture_files,
    write_source_snapshots,
)
from domain_intelligence.capture.contracts import CaptureTarget
from domain_intelligence.models import (
    AcquisitionCapability,
    AcquisitionMethod,
    SourceProfile,
    SourceRole,
)


def _source(source_id: str) -> SourceProfile:
    return SourceProfile(
        id=source_id,
        name="公开来源",
        role=SourceRole.OFFICIAL_PRIMARY,
        acquisition=AcquisitionCapability(
            method=AcquisitionMethod.STATIC_HTML,
            endpoint="https://example.com",
        ),
    )


def test_source_profile_rejects_path_like_id() -> None:
    with pytest.raises(ValidationError):
        _source("../outside")


def test_snapshot_writer_rejects_path_like_id_even_if_model_was_bypassed(
    tmp_path: Path,
) -> None:
    capture_root = tmp_path / "capture"
    capture_root.mkdir()
    source = _source("safe-source").model_copy(update={"id": "../outside"})

    with pytest.raises(UnsafeSourceIdError):
        write_source_snapshots(capture_root, (source,), {})

    assert not (tmp_path / "outside.json").exists()


def test_capture_writer_rejects_content_directory_symlink(tmp_path: Path) -> None:
    capture_root = tmp_path / "capture"
    capture_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (capture_root / "content").symlink_to(outside, target_is_directory=True)
    target = CaptureTarget(_source("safe-source"), "https://example.com", None, None)

    with pytest.raises(UnsafeCapturePathError):
        write_capture_files(capture_root, target, b"raw", "正文", "text/html")

    assert not tuple(outside.iterdir())


def test_capture_writer_rejects_destination_symlink(tmp_path: Path) -> None:
    capture_root = tmp_path / "capture"
    content_root = capture_root / "content"
    content_root.mkdir(parents=True)
    outside = tmp_path / "outside.txt"
    outside.write_text("keep", encoding="utf-8")
    target = CaptureTarget(_source("safe-source"), "https://example.com", None, None)
    text_path = content_root / f"{content_id(target)}.md"
    text_path.symlink_to(outside)

    with pytest.raises(UnsafeCapturePathError):
        write_capture_files(capture_root, target, b"raw", "正文", "text/html")

    assert outside.read_text(encoding="utf-8") == "keep"


def test_public_url_rejects_loopback_literal() -> None:
    with pytest.raises(transport.PublicUrlError) as error:
        transport._validate_public_url("http://127.0.0.1:8765/private")

    assert error.value.code == "PRIVATE_OR_RESERVED_HOST"


def test_public_url_rejects_private_dns_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        transport.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("10.0.0.1", 443)),
        ],
    )

    with pytest.raises(transport.PublicUrlError) as error:
        transport._validate_public_url("https://internal.example/private")

    assert error.value.code == "PRIVATE_OR_RESERVED_HOST"


class _FakeStream(AbstractAsyncContextManager[httpx2.Response]):
    def __init__(self, response: httpx2.Response) -> None:
        self.response = response

    async def __aenter__(self) -> httpx2.Response:
        return self.response

    async def __aexit__(self, *args: object) -> None:
        return None


class _FakeClient:
    def __init__(self, responses: Iterator[httpx2.Response]) -> None:
        self.responses = iter(responses)

    def stream(self, *args: object, **kwargs: object) -> _FakeStream:
        del args, kwargs
        return _FakeStream(next(self.responses))


def test_public_request_revalidates_redirect_destination(monkeypatch: pytest.MonkeyPatch) -> None:
    def validate(url: str) -> None:
        if "127.0.0.1" in url:
            raise transport.PublicUrlError(transport.PRIVATE_OR_RESERVED_HOST, url)

    monkeypatch.setattr(transport, "_validate_public_url", validate)
    client = _FakeClient(
        iter(
            [
                httpx2.Response(
                    302,
                    headers={"location": "http://127.0.0.1:8765/private"},
                    content=b"",
                ),
            ],
        ),
    )

    with pytest.raises(transport.PublicUrlError) as error:
        anyio.run(transport._request_public, client, "https://public.example/start", 1024)

    assert error.value.code == "PRIVATE_OR_RESERVED_HOST"


def test_public_request_stops_reading_after_body_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(transport, "_validate_public_url", lambda url: None)
    client = _FakeClient(
        iter(
            [
                httpx2.Response(
                    200,
                    headers={"content-type": "text/plain"},
                    content=b"0123456789",
                    request=httpx2.Request("GET", "https://public.example/start"),
                ),
            ],
        ),
    )

    with pytest.raises(transport.ResponseTooLargeError):
        anyio.run(transport._request_public, client, "https://public.example/start", 3)


def test_public_request_rechecks_dns_before_connecting(monkeypatch: pytest.MonkeyPatch) -> None:
    resolutions = [("93.184.216.34",)]

    def resolve(hostname: str, port: int, url: str) -> tuple[str, ...]:
        del hostname, port, url
        if resolutions:
            return resolutions.pop()
        raise transport.PublicUrlError(
            transport.PRIVATE_OR_RESERVED_HOST, "https://rebind.example/start"
        )

    monkeypatch.setattr(transport, "_resolve_public_addresses", resolve)
    client = transport._create_client()

    try:
        with pytest.raises(transport.PublicUrlError) as error:
            anyio.run(transport._request_public, client, "https://rebind.example/start", 1024)
    finally:
        anyio.run(client.aclose)

    assert error.value.code == "PRIVATE_OR_RESERVED_HOST"
