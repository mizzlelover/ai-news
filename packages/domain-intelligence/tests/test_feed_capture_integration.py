from __future__ import annotations

from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

import pytest

from domain_intelligence.io import load_input
from domain_intelligence.models import (
    AcquisitionMethod,
    BootstrapInput,
    ContentCaptureStatus,
)
from domain_intelligence.public_capture import capture_public_sources

RSS = (
    '<rss version="2.0"><channel><title>数字孪生信号</title>'
    "<item><title>已知政策</title><guid>rss-known</guid>"
    "<link>/rss/known</link><pubDate>Sun, 30 Aug 2026 07:30:00 GMT</pubDate>"
    "<description>预置线索对应条目</description></item>"
    "<item><title>新增项目</title><guid>rss-new</guid>"
    "<link>/rss/new</link><pubDate>Sun, 30 Aug 2026 07:40:00 GMT</pubDate>"
    "<description>新增项目摘要</description></item>"
    "<item><title>重复入口</title><guid>rss-duplicate</guid>"
    "<link>/rss/new</link><pubDate>Sun, 30 Aug 2026 07:41:00 GMT</pubDate></item>"
    "<item><title>过期内容</title><guid>rss-old</guid>"
    "<link>/rss/old</link><pubDate>Fri, 28 Aug 2026 07:00:00 GMT</pubDate></item>"
    "<item><title>未来内容</title><guid>rss-future</guid>"
    "<link>/rss/future</link><pubDate>Sun, 30 Aug 2026 09:00:00 GMT</pubDate></item>"
    "</channel></rss>"
)

ATOM = (
    '<feed xmlns="http://www.w3.org/2005/Atom"><title>项目更新</title>'
    "<entry><id>atom-new</id><title>Atom 新项目</title>"
    '<link href="/atom/new" /><published>2026-08-30T07:35:00Z</published>'
    "<summary>Atom 项目摘要</summary></entry>"
    "<entry><id>atom-failed</id><title>Atom 缺失页</title>"
    '<link href="/atom/missing" /><published>2026-08-30T07:36:00Z</published></entry>'
    "</feed>"
)


def _make_handler() -> type[BaseHTTPRequestHandler]:
    routes = {
        "/rss": ("application/rss+xml; charset=utf-8", RSS),
        "/atom": ("application/atom+xml; charset=utf-8", ATOM),
        "/rss/known": ("text/html; charset=utf-8", "<html><body>已知政策全文</body></html>"),
        "/rss/new": ("text/html; charset=utf-8", "<html><body>新增项目全文</body></html>"),
        "/atom/new": ("text/html; charset=utf-8", "<html><body>Atom 新项目全文</body></html>"),
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


def _inputs(base_url: str) -> BootstrapInput:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    original = load_input(fixture)
    source_by_id = {str(source.id): source for source in original.attention_graph.sources}
    sources = tuple(
        source_by_id[source_id].model_copy(
            update={
                "acquisition": source_by_id[source_id].acquisition.model_copy(
                    update={"method": method, "endpoint": base_url + endpoint},
                ),
            },
        )
        for source_id, method, endpoint in (
            ("official-policy", AcquisitionMethod.RSS, "/rss"),
            ("industry-brief", AcquisitionMethod.ATOM, "/atom"),
        )
    )
    graph = original.attention_graph.model_copy(update={"sources": sources})
    known_signal = next(signal for signal in original.signals if signal.id == "signal-policy")
    known_signal = known_signal.model_copy(update={"url": base_url + "/rss/known"})
    return original.model_copy(update={"attention_graph": graph, "signals": (known_signal,)})


def test_feed_capture_discovers_items_fetches_full_text_and_preserves_seed_signal(
    fixture_server: str,
    tmp_path: Path,
) -> None:
    capture_root = tmp_path / "capture"
    batch = capture_public_sources(_inputs(fixture_server), capture_root)

    assert len(batch.evidence) == 3
    assert len(batch.contents) == 6
    assert sum(item.status is ContentCaptureStatus.CAPTURED for item in batch.contents) == 5
    assert sum(item.status is ContentCaptureStatus.FAILED for item in batch.contents) == 1
    assert {run.status.value for run in batch.runs} == {"succeeded"}
    assert "signal-policy" in {record.id for record in batch.evidence}
    assert any(record.url.endswith("/rss/new") for record in batch.evidence)
    assert any(record.url.endswith("/atom/new") for record in batch.evidence)
    assert not any(record.url.endswith("/rss/old") for record in batch.evidence)
    assert not any(record.url.endswith("/rss/future") for record in batch.evidence)
    assert len({record.url for record in batch.evidence}) == len(batch.evidence)
    assert all(
        record.content_ref is not None and (capture_root / record.content_ref).is_file()
        for record in batch.evidence
    )
    assert all(
        artifact.evidence_id is None
        for artifact in batch.contents
        if artifact.url.endswith("/rss") or artifact.url.endswith("/atom")
    )
    failed = tuple(item for item in batch.contents if item.status is ContentCaptureStatus.FAILED)
    assert len(failed) == 1
    assert failed[0].error_code == "HTTP_404"
