from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from domain_intelligence.models.activation import (
    ActivationReport,
    EvidenceRecord,
    SourceAcquisitionRun,
)
from domain_intelligence.models.core import AttentionGraph, SourceProfile, StrictModel
from domain_intelligence.models.domain import DomainProfile
from domain_intelligence.models.knowledge import KnowledgeGraph
from domain_intelligence.models.outputs import BootstrapReport
from domain_intelligence.models.types import AcquisitionMethod, SourceId


class AcquisitionPlanStatus(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"


class AcquisitionPlanItem(StrictModel):
    source_id: SourceId
    method: AcquisitionMethod
    endpoint: str | None = None
    status: AcquisitionPlanStatus
    reason: str = Field(min_length=1)


class AcquisitionPlan(StrictModel):
    generated_at: datetime
    source_count: int = Field(ge=0)
    items: tuple[AcquisitionPlanItem, ...]


class SnapshotCollectionRequest(StrictModel):
    sources: tuple[SourceProfile, ...]
    snapshot_dir: str = Field(min_length=1)
    as_of: datetime


class AcquisitionBatch(StrictModel):
    runs: tuple[SourceAcquisitionRun, ...]
    evidence: tuple[EvidenceRecord, ...]


class DomainRunManifest(StrictModel):
    run_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    generated_at: datetime
    input_mode: str = Field(min_length=1)
    source_count: int = Field(ge=0)
    ready_source_count: int = Field(ge=0)
    blocked_source_count: int = Field(ge=0)
    evidence_count: int = Field(ge=0)
    signal_count: int = Field(ge=0)
    story_count: int = Field(ge=0)
    artifacts: tuple[str, ...] = Field(min_length=1)


class DomainRunResult(StrictModel):
    manifest: DomainRunManifest
    profile: DomainProfile
    source_map: AttentionGraph
    plan: AcquisitionPlan
    activation: ActivationReport
    knowledge_graph: KnowledgeGraph
    report: BootstrapReport
