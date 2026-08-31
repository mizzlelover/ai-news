from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel

from domain_intelligence.models import (
    AttentionRecommendation,
    BootstrapInput,
    BootstrapReport,
    ContentArtifact,
    ContentCaptureStatus,
    ContentInventory,
    DailyBrief,
    DomainRunResult,
    KnowledgeGraph,
    KnowledgeGraphEdge,
    KnowledgeNodeKind,
    SourceEvaluation,
)


@dataclass(frozen=True, slots=True)
class ContentArchiveMissingError(FileNotFoundError):
    relative_path: str

    def __str__(self) -> str:
        return f"captured content file is missing: {self.relative_path!r}"


@dataclass(frozen=True, slots=True)
class ContentArchivePathError(ValueError):
    relative_path: str

    def __str__(self) -> str:
        return f"content path escapes the capture root: {self.relative_path!r}"


def load_input(path: Path) -> BootstrapInput:
    return BootstrapInput.model_validate_json(path.read_bytes())


def write_json(model: BaseModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2) + "\n", encoding="utf-8")


def _attention_line(item: AttentionRecommendation) -> str:
    experts = ", ".join(item.supporting_expert_ids) or "-"
    return (
        f"| `{item.source_id}` | {item.score:.3f} | {item.cross_cluster_support:.3f} | {experts} |"
    )


def _evaluation_line(item: SourceEvaluation) -> str:
    return (
        f"| `{item.source_id}` | {item.nugget_recall:.3f} | "
        f"{item.precision:.3f} | {item.lead_time_hours:.1f} | "
        f"{item.false_alarm_burden:.3f} |"
    )


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


def render_markdown(report: BootstrapReport) -> str:
    portfolio_sources = (
        ", ".join(str(source_id) for source_id in report.portfolio.selected_source_ids) or "none"
    )
    lines = [
        "# Domain Intelligence Bootstrap Report",
        "",
        f"- Domain: `{report.domain}`",
        f"- Generated at: `{report.generated_at.isoformat()}`",
        (
            f"- Coverage: `{report.coverage.covered_elements}/"
            f"{report.coverage.total_elements}` elements"
        ),
        f"- Portfolio: `{portfolio_sources}`",
        "",
        "## Source activation",
        "",
        f"- Evidence records: `{len(report.activation.evidence)}`",
        f"- Signals considered: `{len(report.signals)}`",
        f"- Signals created by activation: `{len(report.activation.signals)}`",
        f"- Knowledge-domain deltas: `{len(report.activation.knowledge_deltas)}`",
    ]
    for status in sorted({item.status.value for item in report.activation.source_statuses}):
        count = sum(item.status.value == status for item in report.activation.source_statuses)
        lines.append(f"- `{status}` sources: `{count}`")
    lines.extend(
        [
            "",
            "## Attention recommendations",
            "",
            "| Source | Score | Cross-cluster | Supporting experts |",
            "| --- | ---: | ---: | --- |",
        ],
    )
    lines.extend(_attention_line(item) for item in report.attention_recommendations)
    lines.extend(
        [
            "",
            "## Historical replay",
            "",
            "| Source | Nugget recall | Precision | Lead time (h) | False-alarm burden |",
            "| --- | ---: | ---: | ---: | ---: |",
        ],
    )
    lines.extend(_evaluation_line(item) for item in report.evaluations)
    lines.extend(
        [
            "",
            "## Portfolio",
            "",
            f"- Total cost: `{report.portfolio.total_cost:.3f}`",
            f"- Covered nuggets: `{len(report.portfolio.covered_nugget_ids)}`",
            f"- Selected bundles: `{', '.join(report.portfolio.selected_bundle_ids) or 'none'}`",
            "",
            "## Coverage gaps",
            "",
        ],
    )
    for row in report.coverage.rows:
        reasons = ", ".join(reason.value for reason in row.gap_reasons) or "-"
        lines.append(f"- `{row.element_id}`: {row.coverage_ratio:.3f}; gaps: {reasons}")
    lines.extend(["", "## Daily brief", ""])
    for story in report.brief.stories:
        evidence = ", ".join(story.evidence_urls)
        lines.append(f"- **{story.title}** (`{story.event_type}`, score {story.score:.3f})")
        lines.append(f"  Sources: {', '.join(str(source_id) for source_id in story.source_ids)}")
        lines.append(f"  Evidence: {evidence}")
    return "\n".join(lines) + "\n"


def write_markdown(report: BootstrapReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


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


def _content_link(relative_path: str | None, label: str) -> str:
    return f"[{label}]({relative_path})" if relative_path else "-"


def _content_line(item: ContentArtifact) -> str:
    evidence = item.evidence_id or "-"
    return (
        f"| `{item.status.value}` | `{item.source_id}` | `{evidence}` | {item.title} | "
        f"{item.published_at.date().isoformat() if item.published_at else '-'} | "
        f"{item.character_count} | {_content_link(item.relative_path, '全文')} | "
        f"{_content_link(item.raw_relative_path, '原始响应')} |"
    )


def render_content_inventory(inventory: ContentInventory) -> str:
    lines = [
        "# Content Inventory",
        "",
        f"- Generated at: `{inventory.generated_at.isoformat()}`",
        f"- Content artifacts: `{len(inventory.items)}`",
        "",
        "| Status | Source | Evidence | Title | Published | Characters | Text | Raw |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    lines.extend(_content_line(item) for item in inventory.items)
    if not inventory.items:
        lines.append("| `none` | - | - | No content artifacts captured | - | 0 | - | - |")
    return "\n".join(lines) + "\n"


def _safe_content_path(content_root: Path, relative_path: str) -> Path:
    root = content_root.resolve()
    candidate = (content_root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ContentArchivePathError(relative_path) from error
    return candidate


def _copy_content_file(relative_path: str, content_root: Path, output_dir: Path) -> None:
    source = _safe_content_path(content_root, relative_path)
    if not source.is_file():
        raise ContentArchiveMissingError(relative_path)
    target = output_dir / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def write_content_inventory(
    inventory: ContentInventory,
    output_dir: Path,
    content_root: Path | None = None,
) -> None:
    captured = tuple(
        item for item in inventory.items if item.status is ContentCaptureStatus.CAPTURED
    )
    if not captured:
        write_json(inventory, output_dir / "content-inventory.json")
        write_markdown_content(inventory, output_dir / "content-inventory.md")
        return
    if content_root is None:
        missing_root = "<content_root>"
        raise ContentArchiveMissingError(missing_root)
    root = content_root
    for item in captured:
        if item.relative_path is None:
            raise ContentArchiveMissingError(item.id)
        _validate_content_file(item.relative_path, root)
        if item.raw_relative_path is not None:
            _validate_content_file(item.raw_relative_path, root)
    write_json(inventory, output_dir / "content-inventory.json")
    write_markdown_content(inventory, output_dir / "content-inventory.md")
    for item in captured:
        relative_path = item.relative_path
        if relative_path is None:
            raise ContentArchiveMissingError(item.id)
        _copy_content_file(relative_path, root, output_dir)
        if item.raw_relative_path is not None:
            _copy_content_file(item.raw_relative_path, root, output_dir)


def _validate_content_file(relative_path: str, content_root: Path | None) -> None:
    if content_root is None:
        raise ContentArchiveMissingError(relative_path)
    source = _safe_content_path(content_root, relative_path)
    if not source.is_file():
        raise ContentArchiveMissingError(relative_path)


def write_markdown_content(inventory: ContentInventory, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_content_inventory(inventory), encoding="utf-8")


def render_daily_brief(brief: DailyBrief) -> str:
    lines = [
        f"# {brief.domain} Daily Brief",
        "",
        f"- Generated at: `{brief.generated_at.isoformat()}`",
        f"- Window start: `{brief.window_start.isoformat()}`",
        "",
    ]
    for story in brief.stories:
        lines.extend(
            [
                f"## {story.title}",
                "",
                f"- Event type: `{story.event_type}`",
                f"- Score: `{story.score:.3f}`",
                f"- Sources: {', '.join(str(source_id) for source_id in story.source_ids)}",
                f"- Evidence: {', '.join(story.evidence_urls)}",
                "",
            ],
        )
    return "\n".join(lines)


def write_domain_run(
    result: DomainRunResult,
    output_dir: Path,
    content_root: Path | None = None,
) -> None:
    write_json(result.profile, output_dir / "domain-profile.json")
    write_json(result.source_map, output_dir / "source-map.json")
    write_json(result.plan, output_dir / "acquisition-plan.json")
    write_json(result.activation, output_dir / "source-activation.json")
    write_json(result.knowledge_graph, output_dir / "knowledge-graph.json")
    write_knowledge_graph_markdown(result.knowledge_graph, output_dir / "knowledge-graph.md")
    write_json(result.report, output_dir / "bootstrap-report.json")
    write_markdown(result.report, output_dir / "bootstrap-report.md")
    write_json(result.report.brief, output_dir / "daily-brief.json")
    (output_dir / "daily-brief.md").write_text(
        render_daily_brief(result.report.brief),
        encoding="utf-8",
    )
    write_content_inventory(result.content_inventory, output_dir, content_root)
    write_json(result.manifest, output_dir / "run-manifest.json")
