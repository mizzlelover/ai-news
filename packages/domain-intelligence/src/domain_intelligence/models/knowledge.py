from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from domain_intelligence.models.core import StrictModel


class KnowledgeNodeKind(StrEnum):
    DOMAIN = "domain"
    TOPIC = "topic"
    ELEMENT = "element"
    EXPERT = "expert"
    SOURCE = "source"
    EVENT = "event"
    NUGGET = "nugget"
    EVIDENCE = "evidence"


class KnowledgeRelationType(StrEnum):
    CONTAINS = "contains"
    ATTENTION = "attention"
    COVERS_TOPIC = "covers_topic"
    COVERS_ELEMENT = "covers_element"
    PUBLISHES = "publishes"
    ABOUT_TOPIC = "about_topic"
    SUPPORTS_ELEMENT = "supports_element"
    EVIDENCES_EVENT = "evidences_event"
    CONTAINS_NUGGET = "contains_nugget"


class KnowledgeNode(StrictModel):
    id: str = Field(min_length=1)
    kind: KnowledgeNodeKind
    label: str = Field(min_length=1)


class KnowledgeGraphEdge(StrictModel):
    id: str = Field(min_length=1)
    from_node_id: str = Field(min_length=1)
    to_node_id: str = Field(min_length=1)
    relation: KnowledgeRelationType
    detail: str | None = Field(default=None, min_length=1)
    confidence: float = Field(default=1.0, ge=0, le=1)
    observed_at: datetime | None = None
    evidence_url: str | None = Field(default=None, min_length=1)


class KnowledgeGraph(StrictModel):
    generated_at: datetime
    domain: str = Field(min_length=1)
    nodes: tuple[KnowledgeNode, ...]
    edges: tuple[KnowledgeGraphEdge, ...]
