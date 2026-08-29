from __future__ import annotations

from pathlib import Path

import typer

from domain_intelligence.io import load_input, write_json, write_markdown
from domain_intelligence.pipeline import build_bootstrap_report

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def bootstrap(
    input_path: Path = typer.Argument(..., exists=True, readable=True),
    output_dir: Path = typer.Option(Path("out"), "--output-dir", "-o"),
) -> None:
    inputs = load_input(input_path)
    report = build_bootstrap_report(inputs)
    json_path = output_dir / "bootstrap-report.json"
    markdown_path = output_dir / "bootstrap-report.md"
    write_json(report, json_path)
    write_markdown(report, markdown_path)
    typer.echo(f"wrote {json_path}")
    typer.echo(f"wrote {markdown_path}")
