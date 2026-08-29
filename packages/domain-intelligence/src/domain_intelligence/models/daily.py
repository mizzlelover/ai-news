from __future__ import annotations

from datetime import datetime

from pydantic import Field

from domain_intelligence.models.core import SourceProfile, StrictModel
from domain_intelligence.models.domain import DomainProfile
from domain_intelligence.models.types import EventId, SignalId, SourceId, TopicId


class DailySignal(StrictModel):
    id: SignalId = Field(min_length=1)
    source_id: SourceId = Field(min_length=1)
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    published_at: datetime
    available_at: datetime
    topic_ids: tuple[TopicId, ...] = ()
    event_type: str = "general"
    importance: float = Field(default=0.5, ge=0, le=1)
    summary: str = ""
    originality: float = Field(default=0.5, ge=0, le=1)
    confirmed: bool = False
    event_id: EventId | None = None


class DailyStory(StrictModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    primary_source_id: SourceId
    source_ids: tuple[SourceId, ...]
    signal_ids: tuple[SignalId, ...]
    topic_ids: tuple[TopicId, ...]
    event_type: str
    score: float = Field(ge=0, le=1)
    corroboration: float = Field(ge=0, le=1)
    first_party: bool
    evidence_urls: tuple[str, ...]


class DailyBrief(StrictModel):
    generated_at: datetime
    window_start: datetime
    domain: str
    stories: tuple[DailyStory, ...]


class DailyBriefInput(StrictModel):
    profile: DomainProfile
    signals: tuple[DailySignal, ...]
    sources: tuple[SourceProfile, ...]
    as_of: datetime
    window_hours: int = Field(default=24, gt=0, le=720)
    limit: int = Field(default=20, ge=1, le=200)
