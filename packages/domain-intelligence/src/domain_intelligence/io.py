from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel

from domain_intelligence.models import (
    AttentionRecommendation,
    BootstrapInput,
    BootstrapReport,
    DailyBrief,
    DomainRunResult,
    SourceEvaluation,
)


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


def write_domain_run(result: DomainRunResult, output_dir: Path) -> None:
    write_json(result.profile, output_dir / "domain-profile.json")
    write_json(result.source_map, output_dir / "source-map.json")
    write_json(result.plan, output_dir / "acquisition-plan.json")
    write_json(result.activation, output_dir / "source-activation.json")
    write_json(result.knowledge_graph, output_dir / "knowledge-graph.json")
    write_json(result.report, output_dir / "bootstrap-report.json")
    write_markdown(result.report, output_dir / "bootstrap-report.md")
    write_json(result.report.brief, output_dir / "daily-brief.json")
    (output_dir / "daily-brief.md").write_text(
        render_daily_brief(result.report.brief),
        encoding="utf-8",
    )
    write_json(result.manifest, output_dir / "run-manifest.json")
