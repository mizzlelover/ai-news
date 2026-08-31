from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain_intelligence.models import (
    ActivationReport,
    BootstrapInput,
    KnowledgeGraph,
    KnowledgeGraphEdge,
    KnowledgeNode,
    KnowledgeNodeKind,
    KnowledgeRelationType,
)


@dataclass(frozen=True, slots=True)
class _EdgeSpec:
    from_node_id: str
    to_node_id: str
    relation: KnowledgeRelationType
    confidence: float = 1.0
    detail: str | None = None
    observed_at: datetime | None = None
    evidence_url: str | None = None


class _GraphBuilder:
    __slots__ = ("edges", "nodes", "raw_node_ids")

    nodes: dict[str, KnowledgeNode]
    edges: list[KnowledgeGraphEdge]
    raw_node_ids: dict[str, str]

    def __init__(self) -> None:
        self.nodes = {}
        self.edges = []
        self.raw_node_ids = {}

    def add_node(self, kind: KnowledgeNodeKind, raw_id: str, label: str) -> str:
        node_id = f"{kind.value}:{raw_id}"
        self.nodes[node_id] = KnowledgeNode(id=node_id, kind=kind, label=label)
        self.raw_node_ids.setdefault(raw_id, node_id)
        return node_id

    def add_edge(self, spec: _EdgeSpec) -> None:
        self.edges.append(
            KnowledgeGraphEdge(
                id=f"edge-{len(self.edges) + 1:05d}",
                from_node_id=spec.from_node_id,
                to_node_id=spec.to_node_id,
                relation=spec.relation,
                detail=spec.detail,
                confidence=spec.confidence,
                observed_at=spec.observed_at,
                evidence_url=spec.evidence_url,
            ),
        )

    def finish(self, domain: str, generated_at: datetime) -> KnowledgeGraph:
        return KnowledgeGraph(
            generated_at=generated_at,
            domain=domain,
            nodes=tuple(sorted(self.nodes.values(), key=lambda item: item.id)),
            edges=tuple(self.edges),
        )


def _add_taxonomy(
    builder: _GraphBuilder,
    inputs: BootstrapInput,
    activation: ActivationReport,
    domain_node: str,
) -> None:
    topic_labels = {str(item.topic_id): str(item.topic_id) for item in inputs.profile.topic_weights}
    element_labels = {str(item.id): item.label for item in inputs.profile.elements}
    for source in inputs.attention_graph.sources:
        for topic_id in source.topic_ids:
            topic_labels.setdefault(str(topic_id), str(topic_id))
        for element_id in source.element_ids:
            element_labels.setdefault(str(element_id), str(element_id))
    for record in activation.evidence:
        for topic_id in record.topic_ids:
            topic_labels.setdefault(str(topic_id), str(topic_id))
        for element_id in record.element_ids:
            element_labels.setdefault(str(element_id), str(element_id))
    topic_nodes = {
        topic_id: builder.add_node(KnowledgeNodeKind.TOPIC, topic_id, label)
        for topic_id, label in sorted(topic_labels.items())
    }
    element_nodes = {
        element_id: builder.add_node(KnowledgeNodeKind.ELEMENT, element_id, label)
        for element_id, label in sorted(element_labels.items())
    }
    for node_id in (*topic_nodes.values(), *element_nodes.values()):
        builder.add_edge(_EdgeSpec(domain_node, node_id, KnowledgeRelationType.CONTAINS))


def _add_sources(builder: _GraphBuilder, inputs: BootstrapInput, domain_node: str) -> None:
    for expert in inputs.attention_graph.experts:
        expert_node = builder.add_node(KnowledgeNodeKind.EXPERT, str(expert.id), expert.name)
        builder.add_edge(_EdgeSpec(domain_node, expert_node, KnowledgeRelationType.CONTAINS))
    for source in inputs.attention_graph.sources:
        source_node = builder.add_node(KnowledgeNodeKind.SOURCE, str(source.id), source.name)
        builder.add_edge(_EdgeSpec(domain_node, source_node, KnowledgeRelationType.CONTAINS))
        for topic_id in source.topic_ids:
            topic_node = builder.nodes[f"{KnowledgeNodeKind.TOPIC.value}:{topic_id}"]
            builder.add_edge(
                _EdgeSpec(source_node, topic_node.id, KnowledgeRelationType.COVERS_TOPIC),
            )
        for element_id in source.element_ids:
            element_node = builder.nodes[f"{KnowledgeNodeKind.ELEMENT.value}:{element_id}"]
            builder.add_edge(
                _EdgeSpec(source_node, element_node.id, KnowledgeRelationType.COVERS_ELEMENT),
            )


def _add_attention_edges(builder: _GraphBuilder, inputs: BootstrapInput) -> None:
    for attention_edge in inputs.attention_graph.edges:
        from_node = builder.raw_node_ids.get(attention_edge.from_node_id)
        to_node = builder.raw_node_ids.get(attention_edge.to_node_id)
        if from_node is None or to_node is None:
            continue
        confidence = (
            attention_edge.relation_strength
            * attention_edge.topic_relevance
            * attention_edge.evidence_confidence
        )
        builder.add_edge(
            _EdgeSpec(
                from_node,
                to_node,
                KnowledgeRelationType.ATTENTION,
                confidence=confidence,
                detail=attention_edge.relation.value,
                observed_at=attention_edge.observed_at,
                evidence_url=attention_edge.evidence_url,
            ),
        )


def _add_events(builder: _GraphBuilder, inputs: BootstrapInput, domain_node: str) -> None:
    for event in inputs.benchmark.events:
        event_node = builder.add_node(KnowledgeNodeKind.EVENT, str(event.id), event.title)
        builder.add_edge(_EdgeSpec(domain_node, event_node, KnowledgeRelationType.CONTAINS))
        for nugget in event.nuggets:
            nugget_node = builder.add_node(KnowledgeNodeKind.NUGGET, str(nugget.id), nugget.label)
            builder.add_edge(
                _EdgeSpec(event_node, nugget_node, KnowledgeRelationType.CONTAINS_NUGGET),
            )


def _add_evidence(builder: _GraphBuilder, activation: ActivationReport) -> None:
    for record in activation.evidence:
        evidence_node = builder.add_node(KnowledgeNodeKind.EVIDENCE, record.id, record.title)
        source_node = builder.raw_node_ids[str(record.source_id)]
        builder.add_edge(
            _EdgeSpec(
                source_node,
                evidence_node,
                KnowledgeRelationType.PUBLISHES,
                evidence_url=record.url,
            ),
        )
        for topic_id in record.topic_ids:
            topic_node = builder.nodes[f"{KnowledgeNodeKind.TOPIC.value}:{topic_id}"]
            builder.add_edge(
                _EdgeSpec(evidence_node, topic_node.id, KnowledgeRelationType.ABOUT_TOPIC),
            )
        for element_id in record.element_ids:
            element_node = builder.nodes[f"{KnowledgeNodeKind.ELEMENT.value}:{element_id}"]
            builder.add_edge(
                _EdgeSpec(evidence_node, element_node.id, KnowledgeRelationType.SUPPORTS_ELEMENT),
            )
        if record.event_id is not None:
            event_node = builder.raw_node_ids.get(str(record.event_id))
            if event_node is not None:
                builder.add_edge(
                    _EdgeSpec(
                        evidence_node,
                        event_node,
                        KnowledgeRelationType.EVIDENCES_EVENT,
                        confidence=record.importance,
                        observed_at=record.available_at,
                        evidence_url=record.url,
                    ),
                )


def build_knowledge_graph(inputs: BootstrapInput, activation: ActivationReport) -> KnowledgeGraph:
    builder = _GraphBuilder()
    domain_node = builder.add_node(
        KnowledgeNodeKind.DOMAIN,
        inputs.profile.domain,
        inputs.profile.domain,
    )
    _add_taxonomy(builder, inputs, activation, domain_node)
    _add_sources(builder, inputs, domain_node)
    _add_attention_edges(builder, inputs)
    _add_events(builder, inputs, domain_node)
    _add_evidence(builder, activation)
    return builder.finish(inputs.profile.domain, inputs.as_of)
