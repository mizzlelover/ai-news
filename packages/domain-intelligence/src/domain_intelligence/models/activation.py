from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from domain_intelligence.models.core import SourceProfile, StrictModel
from domain_intelligence.models.daily import DailySignal
from domain_intelligence.models.types import ElementId, EventId, SourceId, TopicId


class AcquisitionRunStatus(StrEnum):
    SUCCEEDED = "succeeded"
    EMPTY = "empty"
    FAILED = "failed"


class ActivationStatus(StrEnum):
    BLOCKED = "blocked"
    READY = "ready"
    OBSERVED = "observed"
    EMPTY = "empty"
    FAILED = "failed"


class KnowledgeChangeType(StrEnum):
    NEW_EVIDENCE = "new_evidence"


class SourceAcquisitionRun(StrictModel):
    id: str = Field(min_length=1)
    source_id: SourceId
    status: AcquisitionRunStatus
    retrieved_at: datetime
    evidence_ids: tuple[str, ...] = ()
    error_code: str | None = Field(default=None, min_length=1)


class EvidenceRecord(StrictModel):
    id: str = Field(min_length=1)
    source_id: SourceId
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    summary: str = ""
    published_at: datetime
    available_at: datetime
    retrieved_at: datetime
    content_hash: str = Field(min_length=1)
    topic_ids: tuple[TopicId, ...] = ()
    element_ids: tuple[ElementId, ...] = ()
    event_type: str = "general"
    importance: float = Field(default=0.5, ge=0, le=1)
    originality: float = Field(default=0.5, ge=0, le=1)
    confirmed: bool = False
    event_id: EventId | None = None


class SourceActivation(StrictModel):
    source_id: SourceId
    status: ActivationStatus
    last_run_at: datetime | None = None
    evidence_count: int = Field(default=0, ge=0)


class KnowledgeDomainDelta(StrictModel):
    evidence_id: str = Field(min_length=1)
    source_id: SourceId
    change_type: KnowledgeChangeType
    topic_ids: tuple[TopicId, ...] = ()
    element_ids: tuple[ElementId, ...] = ()


class ActivationInput(StrictModel):
    sources: tuple[SourceProfile, ...]
    runs: tuple[SourceAcquisitionRun, ...] = ()
    evidence: tuple[EvidenceRecord, ...] = ()
    as_of: datetime
    window_hours: int = Field(default=24, gt=0, le=720)


class ActivationReport(StrictModel):
    generated_at: datetime
    window_start: datetime
    source_statuses: tuple[SourceActivation, ...]
    evidence: tuple[EvidenceRecord, ...]
    signals: tuple[DailySignal, ...]
    knowledge_deltas: tuple[KnowledgeDomainDelta, ...]
