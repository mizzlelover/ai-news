from __future__ import annotations

from pathlib import Path

from domain_intelligence.io_content import write_content_inventory
from domain_intelligence.io_graph import write_knowledge_graph_markdown
from domain_intelligence.io_json import write_json
from domain_intelligence.io_report import render_daily_brief, write_markdown
from domain_intelligence.models import DomainRunResult


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
