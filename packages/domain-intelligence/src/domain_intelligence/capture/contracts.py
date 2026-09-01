from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from domain_intelligence.feed_discovery import FeedItem
from domain_intelligence.models import (
    BootstrapInput,
    ContentArtifact,
    DailySignal,
    EvidenceRecord,
    SourceProfile,
)

MAX_BODY_BYTES = 12_000_000
MAX_CONCURRENT_REQUESTS = 12
USER_AGENT = "PrivateIntelligenceObservatory/0.1 public-capture"


@dataclass(frozen=True, slots=True)
class CaptureTarget:
    source: SourceProfile
    url: str
    signal: DailySignal | None
    evidence_template: EvidenceRecord | None
    feed_item: FeedItem | None = None


@dataclass(frozen=True, slots=True)
class CaptureOutcome:
    artifact: ContentArtifact
    evidence: EvidenceRecord | None
    feed_items: tuple[FeedItem, ...] = ()
    discovery_error_code: str | None = None


@dataclass(frozen=True, slots=True)
class CaptureContext:
    capture_root: Path
    as_of: datetime
    max_body_bytes: int


@dataclass(frozen=True, slots=True)
class CapturedDocument:
    text: str
    content_type: str
    content_hash: str
    relative_path: str


def source_signals(inputs: BootstrapInput) -> dict[str, tuple[DailySignal, ...]]:
    source_ids = {str(source.id) for source in inputs.attention_graph.sources}
    grouped: dict[str, list[DailySignal]] = {}
    for signal in inputs.signals:
        source_id = str(signal.source_id)
        if source_id in source_ids:
            grouped.setdefault(source_id, []).append(signal)
    return {source_id: tuple(signals) for source_id, signals in grouped.items()}
