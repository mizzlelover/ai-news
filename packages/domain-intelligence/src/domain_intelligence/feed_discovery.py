from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

import defusedxml.ElementTree

from domain_intelligence.capture_parser import normalize_text, parse_datetime
from domain_intelligence.models import AcquisitionMethod

XML_BASE = "{http://www.w3.org/XML/1998/namespace}base"


@dataclass(frozen=True, slots=True)
class FeedItem:
    identity: str
    title: str
    url: str
    published_at: datetime | None
    summary: str


@dataclass(frozen=True, slots=True)
class FeedParseError(ValueError):
    error_code: str
    detail: str


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()


def _child(
    element: defusedxml.ElementTree.Element,
    names: frozenset[str],
) -> defusedxml.ElementTree.Element | None:
    return next(
        (candidate for candidate in element if _local_name(candidate.tag) in names),
        None,
    )


def _value(element: defusedxml.ElementTree.Element, names: frozenset[str]) -> str:
    child = _child(element, names)
    return normalize_text(" ".join(child.itertext())) if child is not None else ""


def _date(element: defusedxml.ElementTree.Element, names: frozenset[str]) -> datetime | None:
    value = _value(element, names)
    return parse_datetime(value) if value else None


def _base_url(element: defusedxml.ElementTree.Element, fallback: str) -> str:
    return urljoin(fallback, element.attrib.get(XML_BASE, ""))


def _rss_url(element: defusedxml.ElementTree.Element, base_url: str) -> str:
    value = _value(element, frozenset({"link"}))
    return urljoin(base_url, value) if value else ""


def _atom_url(element: defusedxml.ElementTree.Element, base_url: str) -> str:
    links = tuple(
        child for child in element if _local_name(child.tag) == "link" and child.attrib.get("href")
    )
    link = next(
        (
            candidate
            for candidate in links
            if candidate.attrib.get("rel", "alternate") == "alternate"
        ),
        links[0] if links else None,
    )
    if link is None:
        return ""
    return urljoin(base_url, link.attrib["href"].strip())


def _rss_item(item: defusedxml.ElementTree.Element, base_url: str) -> FeedItem | None:
    url = _rss_url(item, base_url)
    if not url:
        return None
    identity = _value(item, frozenset({"guid", "id"})) or url
    title = _value(item, frozenset({"title"})) or url
    summary = _value(item, frozenset({"description", "summary", "content"}))
    published_at = _date(
        item,
        frozenset({"pubdate", "published", "updated", "date"}),
    )
    return FeedItem(identity, title, url, published_at, summary)


def _atom_item(item: defusedxml.ElementTree.Element, base_url: str) -> FeedItem | None:
    item_base = _base_url(item, base_url)
    url = _atom_url(item, item_base)
    if not url:
        return None
    identity = _value(item, frozenset({"id", "guid"})) or url
    title = _value(item, frozenset({"title"})) or url
    summary = _value(item, frozenset({"summary", "content", "description"}))
    published_at = _date(item, frozenset({"published", "updated", "pubdate", "date"}))
    return FeedItem(identity, title, url, published_at, summary)


def _unique(items: tuple[FeedItem, ...]) -> tuple[FeedItem, ...]:
    seen: set[str] = set()
    result: list[FeedItem] = []
    for item in items:
        key = f"{item.identity}|{item.url}"
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return tuple(result)


def discover_feed_items(
    text: str,
    method: AcquisitionMethod,
    base_url: str,
) -> tuple[FeedItem, ...]:
    if method not in {AcquisitionMethod.RSS, AcquisitionMethod.ATOM}:
        error_code = "FEED_METHOD_UNSUPPORTED"
        raise FeedParseError(error_code, method.value)
    try:
        root = defusedxml.ElementTree.fromstring(text)
    except defusedxml.ElementTree.ParseError as error:
        error_code = "FEED_MALFORMED"
        raise FeedParseError(error_code, str(error)) from error
    root_name = _local_name(root.tag)
    expected_root = "rss" if method is AcquisitionMethod.RSS else "feed"
    if root_name != expected_root:
        error_code = "FEED_ROOT_MISMATCH"
        raise FeedParseError(error_code, f"expected {expected_root}, got {root_name}")
    feed_base = _base_url(root, base_url)
    if method is AcquisitionMethod.RSS:
        container = _child(root, frozenset({"channel"}))
        if container is None:
            container = root
        item_base = _base_url(container, feed_base)
        parsed = tuple(
            item
            for candidate in container
            if _local_name(candidate.tag) == "item"
            if (item := _rss_item(candidate, item_base)) is not None
        )
    else:
        parsed = tuple(
            item
            for candidate in root
            if _local_name(candidate.tag) == "entry"
            if (item := _atom_item(candidate, feed_base)) is not None
        )
    return _unique(parsed)
