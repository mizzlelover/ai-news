from __future__ import annotations

from pydantic import Field

from domain_intelligence.models.core import StrictModel
from domain_intelligence.models.types import ElementId, EventId, IntelligenceMode, TopicId


class EssentialInformationElement(StrictModel):
    id: ElementId = Field(min_length=1)
    label: str = Field(min_length=1)
    topic_id: TopicId = Field(min_length=1)
    weight: float = Field(default=1.0, gt=0)
    required_source_count: int = Field(default=1, ge=1, le=20)


class IntelligenceRequirement(StrictModel):
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    element_ids: tuple[ElementId, ...] = ()
    priority: float = Field(default=1.0, gt=0)


class EventPriority(StrictModel):
    event_type: str = Field(min_length=1)
    weight: float = Field(default=1.0, ge=0, le=1)


class TopicWeight(StrictModel):
    topic_id: TopicId = Field(min_length=1)
    weight: float = Field(default=1.0, ge=0, le=1)


class StopRules(StrictModel):
    minimum_sources_per_element: int = Field(default=1, ge=1, le=20)
    minimum_historical_nugget_recall: float = Field(default=0.85, ge=0, le=1)
    maximum_duplicate_ratio: float = Field(default=0.35, ge=0, le=1)
    saturation_new_source_ratio: float = Field(default=0.05, ge=0, le=1)


class DomainProfile(StrictModel):
    domain: str = Field(min_length=1)
    domain_aliases: tuple[str, ...] = ()
    domain_intent: str | None = Field(default=None, min_length=1)
    mode: IntelligenceMode = IntelligenceMode.DOMAIN_FOUNDATION
    decision_context: str | None = Field(default=None, min_length=1)
    requirements: tuple[IntelligenceRequirement, ...] = ()
    elements: tuple[EssentialInformationElement, ...] = ()
    topic_weights: tuple[TopicWeight, ...] = ()
    event_priorities: tuple[EventPriority, ...] = ()
    stop_rules: StopRules = Field(default_factory=StopRules)


class DomainEvent(StrictModel):
    id: EventId = Field(min_length=1)
    event_type: str = Field(min_length=1)
    topic_ids: tuple[TopicId, ...] = ()
