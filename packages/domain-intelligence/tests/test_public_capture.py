from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import Mock, patch
from urllib.parse import urlparse

import pytest

from domain_intelligence.capture import transport
from domain_intelligence.capture_parser import parse_document
from domain_intelligence.io import load_input
from domain_intelligence.models import BootstrapInput, ContentCaptureStatus
from domain_intelligence.public_capture import capture_public_sources


def _make_handler() -> type[BaseHTTPRequestHandler]:
    routes = {
        "/policy.xml": (
            "text/html; charset=utf-8",
            (
                "<html><head><title>政策入口</title>"
                '<meta property="article:published_time" content="2026-08-30T07:00:00Z">'
                "</head><body><article>政策入口内容, 持续观察数字孪生"
                "政策变化。</article></body></html>"
            ),
        ),
        "/policy": (
            "text/html; charset=utf-8",
            (
                "<html><head><title>政策正文</title></head>"
                '<body><time datetime="2026-08-30T07:00:00Z"></time>'
                "<article>政策正文全文, 包含真实采集后的证据段落。</article></body></html>"
            ),
        ),
        "/industry.xml": (
            "application/xml; charset=utf-8",
            "<feed><title>产业入口</title><entry>产业入口内容</entry></feed>",
        ),
        "/industry/launch": (
            "text/html; charset=utf-8",
            (
                "<html><body><h1>项目落地</h1>"
                "<p>产业项目进入运营, 形成可核验的实施线索。</p></body></html>"
            ),
        ),
        "/overseas.json": (
            "application/json; charset=utf-8",
            '{"title":"海外实践入口","items":["公开项目"]}',
        ),
    }

    class FixtureHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            route = routes.get(urlparse(self.path).path)
            if route is None:
                self.send_error(404)
                return
            content_type, body = route
            encoded = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, fmt: str, *args: str) -> None:
            del fmt, args

    return FixtureHandler


@pytest.fixture
def fixture_server() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _make_handler())
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def _local_inputs(base_url: str) -> BootstrapInput:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    inputs = load_input(fixture)
    endpoint_paths = {
        "official-policy": "/policy.xml",
        "industry-brief": "/industry.xml",
        "overseas-watch": "/missing",
    }
    sources = tuple(
        source.model_copy(
            update={
                "acquisition": source.acquisition.model_copy(
                    update={"endpoint": base_url + endpoint_paths[str(source.id)]},
                ),
            },
        )
        for source in inputs.attention_graph.sources
    )
    signals = tuple(
        signal.model_copy(
            update={
                "url": base_url
                + {"signal-policy": "/policy", "signal-market": "/industry/launch"}[str(signal.id)],
            },
        )
        for signal in inputs.signals
    )
    return inputs.model_copy(
        update={
            "attention_graph": inputs.attention_graph.model_copy(update={"sources": sources}),
            "signals": signals,
        },
    )


def test_parser_extracts_visible_text_and_publication_time() -> None:
    document = parse_document(
        "<html><head><title>标题</title>"
        '<meta property="article:published_time" content="2026-08-30T07:00:00Z">'
        "</head><body><script>ignore me</script><p>正文内容</p></body></html>",
        "text/html",
    )

    assert document.title == "标题"
    assert document.text == "正文内容"
    assert document.published_at is not None
    assert document.published_at.isoformat() == "2026-08-30T07:00:00+00:00"


def test_parser_extracts_pdf_text() -> None:
    page = Mock()
    page.extract_text.return_value = "数字孪生标准正文"
    with patch("domain_intelligence.capture_parser.PdfReader") as reader:
        reader.return_value.pages = [page]
        document = parse_document("%PDF-1.7", "application/pdf", b"%PDF-1.7")

    assert document.text == "数字孪生标准正文"


def test_public_capture_writes_content_and_evidence_snapshots(
    fixture_server: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(transport, "_validate_public_url", lambda url: None)
    inputs = _local_inputs(fixture_server)
    capture_root = tmp_path / "capture"

    batch = capture_public_sources(inputs, capture_root)

    assert len(batch.evidence) == 2
    assert {run.status.value for run in batch.runs} == {"succeeded", "failed"}
    assert len(batch.contents) == 5
    assert sum(item.status is ContentCaptureStatus.CAPTURED for item in batch.contents) == 4
    assert sum(item.status is ContentCaptureStatus.FAILED for item in batch.contents) == 1
    assert all(
        item.relative_path
        for item in batch.contents
        if item.status is ContentCaptureStatus.CAPTURED
    )
    assert all(
        (capture_root / item.relative_path).is_file()
        for item in batch.contents
        if item.relative_path is not None
    )
    assert all(record.content_ref for record in batch.evidence)
    assert all(record.content_char_count > 0 for record in batch.evidence)
    assert all(
        record.content_hash
        == "sha256:"
        + hashlib.sha256(
            (capture_root / record.content_ref).read_bytes(),
        ).hexdigest()
        for record in batch.evidence
        if record.content_ref is not None
    )
    assert all(
        record.content_char_count
        == len((capture_root / record.content_ref).read_text(encoding="utf-8"))
        for record in batch.evidence
        if record.content_ref is not None
    )
    assert batch.evidence[0].element_ids
    assert (capture_root / "content-inventory.json").is_file()
    assert json.loads((capture_root / "official-policy.json").read_text(encoding="utf-8"))
