from __future__ import annotations

import pytest

from domain_intelligence.feed_discovery import (
    FeedParseError,
    discover_feed_items,
)
from domain_intelligence.models import AcquisitionMethod

RSS_DOCUMENT = (
    '<rss version="2.0"><channel><title>数字孪生观察</title>'
    '<item><title>首条更新</title><guid isPermaLink="false">urn:dt:one</guid>'
    "<link>/stories/one?utm_source=test</link>"
    "<pubDate>Sun, 30 Aug 2026 08:00:00 GMT</pubDate><description>首条摘要</description></item>"
    "<item><title>缺少日期的条目</title><link>https://example.test/stories/two</link></item>"
    "</channel></rss>"
)

ATOM_DOCUMENT = (
    '<feed xmlns="http://www.w3.org/2005/Atom" xml:base="https://example.test/atom/">'
    "<title>数字孪生 Atom</title><entry>"
    "<id>tag:example.test,2026:atom-one</id><title>Atom 首条</title>"
    '<link rel="alternate" href="one" /><published>2026-08-30T09:00:00Z</published>'
    "<summary>Atom 摘要</summary></entry></feed>"
)


def test_rss_discovery_extracts_identity_url_title_and_date() -> None:
    items = discover_feed_items(RSS_DOCUMENT, AcquisitionMethod.RSS, "https://example.test/feed")

    assert len(items) == 2
    assert items[0].identity == "urn:dt:one"
    assert items[0].url == "https://example.test/stories/one?utm_source=test"
    assert items[0].title == "首条更新"
    assert items[0].published_at is not None
    assert items[0].published_at.isoformat() == "2026-08-30T08:00:00+00:00"
    assert items[0].summary == "首条摘要"
    assert items[1].published_at is None


def test_atom_discovery_resolves_namespace_and_xml_base() -> None:
    items = discover_feed_items(ATOM_DOCUMENT, AcquisitionMethod.ATOM, "https://fallback.test/feed")

    assert len(items) == 1
    assert items[0].identity == "tag:example.test,2026:atom-one"
    assert items[0].url == "https://example.test/atom/one"
    assert items[0].published_at is not None
    assert items[0].summary == "Atom 摘要"


@pytest.mark.parametrize(
    ("method", "document", "error_code"),
    [
        (AcquisitionMethod.RSS, "<not-valid", "FEED_MALFORMED"),
        (AcquisitionMethod.ATOM, "<rss><channel /></rss>", "FEED_ROOT_MISMATCH"),
        (AcquisitionMethod.JSON, "{}", "FEED_METHOD_UNSUPPORTED"),
    ],
)
def test_feed_discovery_reports_typed_parse_errors(
    method: AcquisitionMethod,
    document: str,
    error_code: str,
) -> None:
    with pytest.raises(FeedParseError) as error:
        discover_feed_items(document, method, "https://example.test/feed")

    assert error.value.error_code == error_code
