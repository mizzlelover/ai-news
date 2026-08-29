from __future__ import annotations

from datetime import datetime

from pydantic import Field

from domain_intelligence.models.core import SourceProfile, StrictModel
from domain_intelligence.models.types import EventId, NuggetId, SourceId, SourceRole


class InformationNugget(StrictModel):
    id: NuggetId = Field(min_length=1)
    event_id: EventId = Field(min_length=1)
    label: str = Field(min_length=1)
    importance: float = Field(default=1.0, gt=0)
    available_at: datetime
    authoritative_at: datetime


class BenchmarkEvent(StrictModel):
    id: EventId = Field(min_length=1)
    title: str = Field(min_length=1)
    nuggets: tuple[InformationNugget, ...] = ()
    importance: float = Field(default=1.0, gt=0)


class Observation(StrictModel):
    id: str = Field(min_length=1)
    source_id: SourceId = Field(min_length=1)
    event_id: EventId | None = None
    nugget_id: NuggetId | None = None
    available_at: datetime
    publication_at: datetime
    is_original: bool = False
    is_confirmed: bool = False
    explanation_depth: float = Field(default=0, ge=0, le=1)
    decision_utility: float = Field(default=0, ge=0, le=1)
    role: SourceRole | None = None
    evidence_url: str | None = None


class TemporalBenchmark(StrictModel):
    events: tuple[BenchmarkEvent, ...]
    sources: tuple[SourceProfile, ...]
    observations: tuple[Observation, ...]
    cutoffs: tuple[datetime, ...] = Field(min_length=1)


class ReplayInput(StrictModel):
    benchmark: TemporalBenchmark


class ReplayCell(StrictModel):
    cutoff: datetime
    event_id: EventId
    nugget_id: NuggetId
    eligible: bool
    visible_source_ids: tuple[SourceId, ...] = ()
    first_source_id: SourceId | None = None


class SourceEvaluation(StrictModel):
    source_id: SourceId
    event_recall: float = Field(default=0, ge=0, le=1)
    nugget_recall: float = Field(default=0, ge=0, le=1)
    lead_time_hours: float = Field(default=0, ge=0)
    precision: float = Field(default=0, ge=0, le=1)
    false_alarm_burden: float = Field(default=0, ge=0, le=1)
    originality: float = Field(default=0, ge=0, le=1)
    credibility: float = Field(default=0, ge=0, le=1)
    explanatory_depth: float = Field(default=0, ge=0, le=1)
    cross_role_confirmation: float = Field(default=0, ge=0, le=1)
    acquisition_reliability: float = Field(default=0, ge=0, le=1)
    decision_utility: float = Field(default=0, ge=0, le=1)
    covered_nugget_ids: tuple[NuggetId, ...] = ()


class ReplayReport(StrictModel):
    cutoffs: tuple[datetime, ...]
    cells: tuple[ReplayCell, ...]
    source_metrics: tuple[SourceEvaluation, ...]
