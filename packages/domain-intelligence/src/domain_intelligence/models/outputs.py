from __future__ import annotations

from datetime import datetime

from pydantic import Field

from domain_intelligence.models.activation import (
    ActivationReport,
    EvidenceRecord,
    SourceAcquisitionRun,
)
from domain_intelligence.models.core import (
    AttentionGraph,
    AttentionQuery,
    ScoreComponent,
    SourceProfile,
    StrictModel,
)
from domain_intelligence.models.daily import DailyBrief, DailySignal
from domain_intelligence.models.domain import DomainProfile
from domain_intelligence.models.knowledge import KnowledgeGraph
from domain_intelligence.models.temporal import (
    ReplayReport,
    SourceEvaluation,
    TemporalBenchmark,
)
from domain_intelligence.models.types import ElementId, GapReason, SourceId


class AttentionRecommendation(StrictModel):
    source_id: SourceId
    score: float = Field(ge=0, le=1)
    cross_cluster_support: float = Field(ge=0, le=1)
    supporting_expert_ids: tuple[str, ...] = ()
    components: tuple[ScoreComponent, ...] = ()


class CoverageRow(StrictModel):
    element_id: ElementId
    coverage_ratio: float = Field(ge=0, le=1)
    source_ids: tuple[SourceId, ...] = ()
    gap_reasons: tuple[GapReason, ...] = ()


class CoverageInput(StrictModel):
    profile: DomainProfile
    sources: tuple[SourceProfile, ...]
    evaluations: tuple[SourceEvaluation, ...] = ()


class CoverageReport(StrictModel):
    total_elements: int = Field(ge=0)
    covered_elements: int = Field(ge=0)
    weighted_coverage: float = Field(ge=0, le=1)
    rows: tuple[CoverageRow, ...]


class SourceBundle(StrictModel):
    id: str = Field(min_length=1)
    source_ids: tuple[SourceId, ...] = Field(min_length=2)
    synergy_bonus: float = Field(default=0, ge=0, le=1)


class PortfolioInput(StrictModel):
    sources: tuple[SourceProfile, ...]
    evaluations: tuple[SourceEvaluation, ...]
    bundles: tuple[SourceBundle, ...] = ()
    budget: float = Field(gt=0)
    max_sources: int = Field(default=20, ge=1, le=200)
    total_nuggets: int = Field(default=0, ge=0)


class PortfolioResult(StrictModel):
    selected_source_ids: tuple[SourceId, ...]
    selected_bundle_ids: tuple[str, ...] = ()
    total_cost: float = Field(ge=0)
    covered_nugget_ids: tuple[str, ...] = ()
    score: float = Field(ge=0)
    marginal_contributions: tuple[str, ...] = ()


class BootstrapInput(StrictModel):
    profile: DomainProfile
    attention_graph: AttentionGraph
    attention_query: AttentionQuery
    benchmark: TemporalBenchmark
    signals: tuple[DailySignal, ...] = ()
    acquisition_runs: tuple[SourceAcquisitionRun, ...] = ()
    evidence: tuple[EvidenceRecord, ...] = ()
    budget: float = Field(default=10.0, gt=0)
    max_sources: int = Field(default=10, ge=1, le=200)
    bundles: tuple[SourceBundle, ...] = ()
    as_of: datetime
    window_hours: int = Field(default=24, gt=0, le=720)
    daily_limit: int = Field(default=20, ge=1, le=200)


class BootstrapReport(StrictModel):
    generated_at: datetime
    domain: str
    knowledge_graph: KnowledgeGraph
    activation: ActivationReport
    signals: tuple[DailySignal, ...]
    attention_recommendations: tuple[AttentionRecommendation, ...]
    replay: ReplayReport
    evaluations: tuple[SourceEvaluation, ...]
    portfolio: PortfolioResult
    coverage: CoverageReport
    brief: DailyBrief
