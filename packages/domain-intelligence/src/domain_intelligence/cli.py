from __future__ import annotations

from pathlib import Path

import typer

from domain_intelligence.io import load_input, write_domain_run, write_json, write_markdown
from domain_intelligence.models import SnapshotCollectionRequest
from domain_intelligence.pipeline import build_bootstrap_report
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
        exists=True,
        file_okay=False,
        readable=True,
        help="Local source snapshots used to execute the acquisition boundary.",
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
        result = build_domain_run(domain, inputs, acquisition)
        write_domain_run(result, output_dir)
        typer.echo(f"wrote {output_dir / 'run-manifest.json'}")
        return
    if bundle_path is not None:
        message = "--bundle requires --domain"
        raise typer.BadParameter(message)
    if snapshot_dir is not None:
        message = "--snapshots requires --domain"
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
