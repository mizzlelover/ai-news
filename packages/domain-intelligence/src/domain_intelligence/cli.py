from __future__ import annotations

from pathlib import Path

import typer

from domain_intelligence.io import load_input, write_domain_run, write_json, write_markdown
from domain_intelligence.models import SnapshotCollectionRequest
from domain_intelligence.pipeline import build_bootstrap_report
from domain_intelligence.public_capture import capture_public_sources
from domain_intelligence.run import build_domain_run
from domain_intelligence.snapshot import collect_snapshots

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def bootstrap(
    input_path: Path | None = typer.Argument(None, exists=True, readable=True),
    output_dir: Path = typer.Option(Path("out"), "--output-dir", "-o"),
    domain: str | None = typer.Option(
        None,
        "--domain",
        help="Run the complete domain workflow from a Skill-generated seed Bundle.",
    ),
    bundle_path: Path | None = typer.Option(
        None,
        "--bundle",
        exists=True,
        readable=True,
        help="Typed seed Bundle used by the domain workflow.",
    ),
    snapshot_dir: Path | None = typer.Option(
        None,
        "--snapshots",
        file_okay=False,
        help="Existing snapshots, or the capture directory used with --fetch.",
    ),
    fetch_live: bool = typer.Option(
        False,
        "--fetch",
        help="Fetch configured public endpoints and archive their content locally.",
    ),
) -> None:
    if domain is not None:
        if input_path is not None:
            message = "use --bundle instead of a positional input file with --domain"
            raise typer.BadParameter(message)
        if bundle_path is None:
            message = "--bundle is required with --domain"
            raise typer.BadParameter(message)
        inputs = load_input(bundle_path)
        if fetch_live:
            capture_dir = snapshot_dir or output_dir / "capture"
            acquisition = capture_public_sources(inputs, capture_dir)
            result = build_domain_run(
                domain,
                inputs.model_copy(update={"signals": ()}),
                acquisition,
                input_mode="domain_seed_bundle_live_capture",
            )
            write_domain_run(result, output_dir, content_root=capture_dir)
        else:
            if snapshot_dir is not None and not snapshot_dir.is_dir():
                message = "--snapshots must point to an existing directory"
                raise typer.BadParameter(message)
            acquisition = (
                collect_snapshots(
                    SnapshotCollectionRequest(
                        sources=inputs.attention_graph.sources,
                        snapshot_dir=str(snapshot_dir),
                        as_of=inputs.as_of,
                    ),
                )
                if snapshot_dir is not None
                else None
            )
            result = build_domain_run(
                domain,
                inputs,
                acquisition,
                input_mode=(
                    "domain_seed_bundle_snapshot"
                    if snapshot_dir is not None
                    else "domain_seed_bundle"
                ),
            )
            write_domain_run(result, output_dir, content_root=snapshot_dir)
        typer.echo(f"wrote {output_dir / 'run-manifest.json'}")
        return
    if bundle_path is not None:
        message = "--bundle requires --domain"
        raise typer.BadParameter(message)
    if snapshot_dir is not None:
        message = "--snapshots requires --domain"
        raise typer.BadParameter(message)
    if fetch_live:
        message = "--fetch requires --domain"
        raise typer.BadParameter(message)
    if input_path is None:
        message = "provide an input Bundle or use --domain with --bundle"
        raise typer.BadParameter(message)
    inputs = load_input(input_path)
    report = build_bootstrap_report(inputs)
    json_path = output_dir / "bootstrap-report.json"
    markdown_path = output_dir / "bootstrap-report.md"
    write_json(report, json_path)
    write_markdown(report, markdown_path)
    typer.echo(f"wrote {json_path}")
    typer.echo(f"wrote {markdown_path}")
