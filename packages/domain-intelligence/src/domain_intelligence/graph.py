from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Final

from domain_intelligence.models import (
    AttentionEdge,
    AttentionGraph,
    AttentionQuery,
    AttentionRecommendation,
    ExpertProfile,
    RelationType,
    ScoreComponent,
    SourceId,
    SourceProfile,
)

RELATION_WEIGHTS: Final[dict[RelationType, float]] = {
    RelationType.EXPLICITLY_RECOMMENDS: 1.0,
    RelationType.CITES: 0.85,
    RelationType.FOLLOWS: 0.65,
    RelationType.STARS: 0.55,
    RelationType.LINKS_TO: 0.5,
    RelationType.APPEARS_WITH: 0.25,
}


@dataclass(frozen=True, slots=True)
class _GraphEdges:
    adjacency: dict[str, list[tuple[str, float]]]
    incoming: dict[SourceId, list[AttentionEdge]]


@dataclass(frozen=True, slots=True)
class _RecommendationContext:
    incoming: dict[SourceId, list[AttentionEdge]]
    expert_by_id: dict[str, ExpertProfile]
    community_count: int
    raw_network: dict[SourceId, float]
    maximum_network: float


def _edge_weight(edge: AttentionEdge, query: AttentionQuery) -> float:
    relation = edge.relation
    days = max(0.0, (query.as_of - edge.observed_at).total_seconds() / 86400)
    decay = math.exp(-math.log(2) * days / query.half_life_days)
    return (
        RELATION_WEIGHTS[relation]
        * edge.relation_strength
        * edge.topic_relevance
        * edge.evidence_confidence
        * decay
    )


def _build_graph_edges(graph: AttentionGraph, query: AttentionQuery) -> _GraphEdges:
    expert_ids = {expert.id for expert in graph.experts}
    source_by_id = {source.id: source for source in graph.sources}
    node_ids = tuple(expert_ids | set(source_by_id))
    adjacency: dict[str, list[tuple[str, float]]] = defaultdict(list)
    incoming: dict[SourceId, list[AttentionEdge]] = defaultdict(list)
    for edge in graph.edges:
        if (
            edge.from_node_id not in node_ids
            or edge.to_node_id not in node_ids
            or edge.observed_at > query.as_of
        ):
            continue
        weight = _edge_weight(edge, query)
        if edge.to_node_id in source_by_id and query.topic_ids:
            source_topics = source_by_id[edge.to_node_id].topic_ids
            if source_topics:
                topic_factor = 1.0 if set(source_topics) & set(query.topic_ids) else 0.2
            else:
                topic_factor = 0.5
            weight *= topic_factor
        if weight <= 0:
            continue
        adjacency[edge.from_node_id].append((edge.to_node_id, weight))
        if edge.to_node_id in source_by_id and edge.from_node_id in expert_ids:
            incoming[edge.to_node_id].append(edge)
    return _GraphEdges(adjacency=dict(adjacency), incoming=dict(incoming))


def _personalized_ranks(
    node_ids: tuple[str, ...],
    seeds: tuple[str, ...],
    adjacency: dict[str, list[tuple[str, float]]],
    query: AttentionQuery,
) -> dict[str, float]:
    seed_mass = 1 / len(seeds)
    personalization = {node: seed_mass if node in seeds else 0.0 for node in node_ids}
    ranks = personalization.copy()
    for _ in range(query.iterations):
        next_ranks = {node: (1 - query.damping) * personalization[node] for node in node_ids}
        dangling = sum(ranks[node] for node in node_ids if not adjacency.get(node))
        for node, targets in adjacency.items():
            total_weight = sum(weight for _, weight in targets)
            if total_weight <= 0:
                continue
            share = query.damping * ranks[node] / total_weight
            for target, weight in targets:
                next_ranks[target] += share * weight
        for seed in seeds:
            next_ranks[seed] += query.damping * dangling * seed_mass
        ranks = next_ranks
    return ranks


def _network_scores(
    source_ids: tuple[SourceId, ...],
    incoming: dict[SourceId, list[AttentionEdge]],
    ranks: dict[str, float],
) -> tuple[dict[SourceId, float], float]:
    raw_network = {
        source_id: ranks.get(source_id, 0.0) / math.sqrt(len(incoming.get(source_id, ())) + 1)
        for source_id in source_ids
    }
    return raw_network, max(raw_network.values(), default=1.0) or 1.0


def _recommendation(
    source_id: SourceId,
    source: SourceProfile,
    context: _RecommendationContext,
) -> AttentionRecommendation:
    source_edges = context.incoming.get(source_id, [])
    supporters = tuple(sorted({edge.from_node_id for edge in source_edges}))
    supported_communities = {
        context.expert_by_id[expert_id].community
        for expert_id in supporters
        if expert_id in context.expert_by_id
    }
    cross_cluster = len(supported_communities) / max(1, context.community_count)
    topic_proximity = (
        sum(edge.topic_relevance * edge.evidence_confidence for edge in source_edges)
        / len(source_edges)
        if source_edges
        else 0.0
    )
    independent_attention = min(1.0, len(supporters) / 3)
    novelty = 1 / (1 + max(0, len(source_edges) - 1) * 0.5)
    network = context.raw_network[source_id] / context.maximum_network
    score = (
        0.25 * network
        + 0.2 * topic_proximity
        + 0.2 * source.authority
        + 0.2 * cross_cluster
        + 0.1 * novelty
        + 0.05 * independent_attention
    )
    components = tuple(
        ScoreComponent(name=name, value=round(value, 6))
        for name, value in (
            ("network", network),
            ("topic_proximity", topic_proximity),
            ("authority", source.authority),
            ("cross_cluster", cross_cluster),
            ("novelty", novelty),
            ("independent_attention", independent_attention),
        )
    )
    return AttentionRecommendation(
        source_id=source_id,
        score=round(score, 6),
        cross_cluster_support=round(cross_cluster, 6),
        supporting_expert_ids=supporters,
        components=components,
    )


def rank_attention_sources(
    graph: AttentionGraph,
    query: AttentionQuery,
) -> tuple[AttentionRecommendation, ...]:
    expert_ids = {expert.id for expert in graph.experts}
    source_by_id = {source.id: source for source in graph.sources}
    seeds = tuple(seed for seed in query.seed_expert_ids if seed in expert_ids)
    if not seeds:
        return ()
    node_ids = tuple(expert_ids | set(source_by_id))
    edges = _build_graph_edges(graph, query)
    ranks = _personalized_ranks(node_ids, seeds, edges.adjacency, query)
    raw_network, maximum_network = _network_scores(tuple(source_by_id), edges.incoming, ranks)
    context = _RecommendationContext(
        incoming=edges.incoming,
        expert_by_id={expert.id: expert for expert in graph.experts},
        community_count=len({expert.community for expert in graph.experts}),
        raw_network=raw_network,
        maximum_network=maximum_network,
    )
    recommendations = tuple(
        _recommendation(source_id, source, context) for source_id, source in source_by_id.items()
    )
    return tuple(sorted(recommendations, key=lambda item: (-item.score, item.source_id)))[
        : query.max_results
    ]
