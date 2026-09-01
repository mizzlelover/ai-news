from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from domain_intelligence.capture.contracts import CaptureOutcome, CaptureTarget
from domain_intelligence.models import (
    ContentArtifact,
    ContentCaptureStatus,
    ContentInventory,
    SourceProfile,
)


def content_id(target: CaptureTarget) -> str:
    signal_id = target.signal.id if target.signal is not None else ""
    feed_identity = target.feed_item.identity if target.feed_item is not None else ""
    digest = hashlib.sha256(
        f"{target.source.id}|{target.url}|{signal_id}|{feed_identity}".encode(),
    ).hexdigest()[:16]
    source = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(target.source.id)).strip("-") or "source"
    return f"content-{source}-{digest}"


def raw_extension(content_type: str) -> str:
    normalized_type = content_type.casefold()
    if "pdf" in normalized_type:
        return ".pdf"
    if "json" in normalized_type:
        return ".json"
    if "xml" in normalized_type or "rss" in normalized_type or "atom" in normalized_type:
        return ".xml"
    if "html" in normalized_type:
        return ".html"
    return ".txt"


def normalize_content_text(text: str) -> str:
    return text.rstrip("\r\n") + "\n"


def failure(
    target: CaptureTarget,
    as_of: datetime,
    status: ContentCaptureStatus,
    error_code: str,
    content_type: str = "application/octet-stream",
) -> CaptureOutcome:
    title = (
        target.feed_item.title
        if target.feed_item is not None
        else target.signal.title
        if target.signal is not None
        else target.source.name
    )
    artifact = ContentArtifact(
        id=content_id(target),
        source_id=target.source.id,
        title=title,
        url=target.url,
        captured_at=as_of,
        content_type=content_type,
        status=status,
        error_code=error_code,
    )
    return CaptureOutcome(artifact=artifact, evidence=None)


def write_capture_files(
    capture_root: Path,
    target: CaptureTarget,
    body: bytes,
    text: str,
    content_type: str,
) -> tuple[str, str]:
    content_dir = capture_root / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    current_id = content_id(target)
    text_relative_path = f"content/{current_id}.md"
    raw_relative_path = f"content/{current_id}{raw_extension(content_type)}"
    (capture_root / text_relative_path).write_text(
        normalize_content_text(text),
        encoding="utf-8",
    )
    (capture_root / raw_relative_path).write_bytes(body)
    return text_relative_path, raw_relative_path


def write_source_snapshots(
    capture_root: Path,
    sources: tuple[SourceProfile, ...],
    outcomes_by_source: dict[str, tuple[CaptureOutcome, ...]],
) -> None:
    for source in sources:
        evidence = tuple(
            outcome.evidence
            for outcome in outcomes_by_source.get(str(source.id), ())
            if outcome.evidence is not None
        )
        payload = [record.model_dump(mode="json") for record in evidence]
        (capture_root / f"{source.id}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def write_capture_inventory(
    capture_root: Path,
    as_of: datetime,
    artifacts: tuple[ContentArtifact, ...],
) -> None:
    inventory = ContentInventory(generated_at=as_of, items=artifacts)
    (capture_root / "content-inventory.json").write_text(
        inventory.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
