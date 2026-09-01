from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import DependencyError, PdfReadError, PyPdfError


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    title: str
    text: str
    published_at: datetime | None


class _VisibleTextParser(HTMLParser):
    _SKIPPED_TAGS = frozenset({"script", "style", "noscript", "template", "svg"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.meta_title = ""
        self.published_values: list[str] = []
        self._skip_depth = 0
        self._title_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.casefold()
        if normalized_tag in self._SKIPPED_TAGS:
            self._skip_depth += 1
        if normalized_tag == "title":
            self._title_depth += 1
        attr_map = {key.casefold(): value or "" for key, value in attrs}
        if normalized_tag == "meta":
            key = attr_map.get("property", "") or attr_map.get("name", "")
            value = attr_map.get("content", "").strip()
            if key.casefold() in {"og:title", "twitter:title"} and value:
                self.meta_title = value
            if (
                key.casefold()
                in {
                    "article:published_time",
                    "og:published_time",
                    "date",
                    "pubdate",
                    "publishdate",
                }
                and value
            ):
                self.published_values.append(value)
        if normalized_tag == "time":
            value = attr_map.get("datetime", "").strip()
            if value:
                self.published_values.append(value)

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.casefold()
        if normalized_tag == "title" and self._title_depth:
            self._title_depth -= 1
        if normalized_tag in self._SKIPPED_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if not value:
            return
        if self._title_depth:
            self.title_parts.append(value)
        if not self._skip_depth and not self._title_depth:
            self.text_parts.append(value)


def parse_datetime(value: str) -> datetime | None:
    candidate = value.strip()
    if not candidate:
        return None
    normalized = candidate[:-1] + "+00:00" if candidate.endswith("Z") else candidate
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        try:
            parsed = parsedate_to_datetime(candidate)
        except (TypeError, ValueError, OverflowError):
            parsed = None
    if parsed is not None:
        return parsed.replace(tzinfo=parsed.tzinfo or UTC)
    match = re.search(r"\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2})\b", candidate)
    if match is None:
        return None
    try:
        return datetime.strptime(match.group(1).replace("/", "-"), "%Y-%m-%d").replace(
            tzinfo=UTC,
        )
    except ValueError:
        return None


def normalize_text(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _parse_json(text: str) -> ParsedDocument:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return ParsedDocument(title="", text=normalize_text(text), published_at=None)
    formatted = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    return ParsedDocument(title="", text=formatted, published_at=None)


def _parse_pdf(body: bytes) -> ParsedDocument:
    try:
        reader = PdfReader(BytesIO(body))
        text = normalize_text("\n".join(page.extract_text() or "" for page in reader.pages))
    except (DependencyError, OSError, PdfReadError, PyPdfError, ValueError):
        text = ""
    return ParsedDocument(title="", text=text, published_at=None)


def parse_document(text: str, content_type: str, body: bytes | None = None) -> ParsedDocument:
    normalized_type = content_type.casefold()
    if "pdf" in normalized_type and body:
        parsed = _parse_pdf(body)
        if parsed.text:
            return parsed
    if "json" in normalized_type:
        parsed = _parse_json(text)
        return ParsedDocument(
            title=parsed.title,
            text=normalize_text(parsed.text),
            published_at=parsed.published_at,
        )
    parser = _VisibleTextParser()
    parser.feed(text)
    parser.close()
    title = parser.meta_title or " ".join(parser.title_parts)
    text_value = normalize_text("\n".join(parser.text_parts))
    if not text_value and "html" not in normalized_type and "xml" not in normalized_type:
        text_value = normalize_text(text)
    published_at = next(
        (parsed for value in parser.published_values if (parsed := parse_datetime(value))),
        None,
    )
    return ParsedDocument(title=title.strip(), text=text_value, published_at=published_at)
