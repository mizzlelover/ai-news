from __future__ import annotations

from pathlib import Path

from domain_intelligence.models import KnowledgeGraph, KnowledgeGraphEdge, KnowledgeNodeKind


def _evidence_trace_line(edge: KnowledgeGraphEdge, node_labels: dict[str, str]) -> str:
    if edge.from_node_id.startswith("evidence:"):
        evidence_id = edge.from_node_id
        related_id = edge.to_node_id
    else:
        evidence_id = edge.to_node_id
        related_id = edge.from_node_id
    related_label = node_labels.get(related_id, related_id)
    return (
        f"| `{evidence_id}` | {related_label} | `"
        f"{edge.relation.value}` | {edge.confidence:.3f} | {edge.evidence_url or '-'} |"
    )


def render_knowledge_graph(graph: KnowledgeGraph) -> str:
    node_labels = {node.id: node.label for node in graph.nodes}
    node_counts = {
        kind.value: sum(node.kind is kind for node in graph.nodes) for kind in KnowledgeNodeKind
    }
    relation_counts: dict[str, int] = {}
    for edge in graph.edges:
        relation_counts[edge.relation.value] = relation_counts.get(edge.relation.value, 0) + 1
    lines = [
        "# Knowledge Graph",
        "",
        f"- Domain: `{graph.domain}`",
        f"- Generated at: `{graph.generated_at.isoformat()}`",
        f"- Nodes: `{len(graph.nodes)}`",
        f"- Edges: `{len(graph.edges)}`",
        "",
        "## Node counts",
        "",
        "| Kind | Count |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{kind}` | {count} |" for kind, count in sorted(node_counts.items()) if count)
    lines.extend(["", "## Relation counts", "", "| Relation | Count |", "| --- | ---: |"])
    lines.extend(
        f"| `{relation}` | {count} |" for relation, count in sorted(relation_counts.items())
    )
    lines.extend(
        [
            "",
            "## Evidence trace",
            "",
            "| Evidence | Source/target | Relation | Confidence | URL |",
            "| --- | --- | --- | ---: | --- |",
        ],
    )
    evidence_edges = tuple(
        edge
        for edge in graph.edges
        if edge.from_node_id.startswith("evidence:") or edge.to_node_id.startswith("evidence:")
    )
    lines.extend(_evidence_trace_line(edge, node_labels) for edge in evidence_edges)
    if not evidence_edges:
        lines.append("| - | No evidence edges | - | 0.000 | - |")
    graph_note = (
        "The complete typed graph is in `knowledge-graph.json`; "
        "this file is the human-readable trace summary."
    )
    lines.extend(["", graph_note])
    return "\n".join(lines) + "\n"


def write_knowledge_graph_markdown(graph: KnowledgeGraph, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_knowledge_graph(graph), encoding="utf-8")
