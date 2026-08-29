from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from domain_intelligence.models.types import (
    AcquisitionMethod,
    ElementId,
    ExpertId,
    RelationType,
    SourceId,
    SourceRole,
    TopicId,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class AcquisitionCapability(StrictModel):
    method: AcquisitionMethod
    endpoint: str | None = None
    stable: bool = False


class SourceProfile(StrictModel):
    id: SourceId = Field(min_length=1)
    name: str = Field(min_length=1)
    role: SourceRole
    topic_ids: tuple[TopicId, ...] = ()
    element_ids: tuple[ElementId, ...] = ()
    authority: float = Field(default=0.5, ge=0, le=1)
    reliability: float = Field(default=0.5, ge=0, le=1)
    stability: float = Field(default=0.5, ge=0, le=1)
    accessibility: float = Field(default=0.5, ge=0, le=1)
    cost: float = Field(default=1.0, ge=0)
    approved: bool = True
    acquisition: AcquisitionCapability


class ExpertProfile(StrictModel):
    id: ExpertId = Field(min_length=1)
    name: str = Field(min_length=1)
    community: str = Field(min_length=1)
    topic_ids: tuple[TopicId, ...] = ()


class AttentionEdge(StrictModel):
    from_node_id: str = Field(min_length=1)
    to_node_id: str = Field(min_length=1)
    relation: RelationType
    relation_strength: float = Field(default=1.0, ge=0, le=1)
    topic_relevance: float = Field(default=1.0, ge=0, le=1)
    evidence_confidence: float = Field(default=1.0, ge=0, le=1)
    observed_at: datetime
    evidence_url: str | None = None


class AttentionGraph(StrictModel):
    experts: tuple[ExpertProfile, ...]
    sources: tuple[SourceProfile, ...]
    edges: tuple[AttentionEdge, ...]


class AttentionQuery(StrictModel):
    seed_expert_ids: tuple[ExpertId, ...] = Field(min_length=1)
    topic_ids: tuple[TopicId, ...] = ()
    as_of: datetime
    half_life_days: float = Field(default=180.0, gt=0)
    damping: float = Field(default=0.85, ge=0, lt=1)
    iterations: int = Field(default=20, ge=1, le=100)
    max_results: int = Field(default=20, ge=1, le=200)


class ScoreComponent(StrictModel):
    name: str = Field(min_length=1)
    value: float = Field(ge=0, le=1)
