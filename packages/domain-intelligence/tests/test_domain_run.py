from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from domain_intelligence.io import load_input, write_domain_run
from domain_intelligence.models import (
    AcquisitionBatch,
    ContentArtifact,
    ContentCaptureStatus,
    SnapshotCollectionRequest,
)
from domain_intelligence.run import DomainMismatchError, build_domain_run
from domain_intelligence.snapshot import collect_snapshots


def test_domain_run_builds_all_delivery_artifacts_from_a_domain_seed() -> None:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    inputs = load_input(fixture)

    result = build_domain_run("data-elements", inputs)

    assert result.manifest.domain == "data-elements"
    assert result.manifest.source_count == 3
    assert result.manifest.evidence_count == 2
    assert result.plan.source_count == 3
    assert len(result.knowledge_graph.nodes) >= 10
    assert result.report.knowledge_graph == result.knowledge_graph
    assert "knowledge-graph.json" in result.manifest.artifacts


def test_domain_run_rejects_a_seed_for_another_domain() -> None:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    inputs = load_input(fixture)

    with pytest.raises(DomainMismatchError):
        build_domain_run("different-domain", inputs)


def test_snapshot_collection_runs_every_configured_source(tmp_path: Path) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    inputs = load_input(fixture)
    source = inputs.attention_graph.sources[0]
    snapshot = [record.model_dump(mode="json") for record in inputs.evidence[:1]]
    (tmp_path / f"{source.id}.json").write_text(json.dumps(snapshot), encoding="utf-8")

    batch = collect_snapshots(
        SnapshotCollectionRequest(
            sources=inputs.attention_graph.sources,
            snapshot_dir=str(tmp_path),
            as_of=inputs.as_of,
        ),
    )

    assert len(batch.runs) == 3
    assert batch.runs[0].status.value == "failed"
    assert any(run.status.value == "succeeded" for run in batch.runs)
    assert len(batch.evidence) == 1


def test_domain_run_can_replace_seed_evidence_with_collection_results(tmp_path: Path) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    inputs = load_input(fixture)
    source = inputs.attention_graph.sources[0]
    snapshot = [record.model_dump(mode="json") for record in inputs.evidence[:1]]
    (tmp_path / f"{source.id}.json").write_text(json.dumps(snapshot), encoding="utf-8")
    batch = collect_snapshots(
        SnapshotCollectionRequest(
            sources=inputs.attention_graph.sources,
            snapshot_dir=str(tmp_path),
            as_of=inputs.as_of,
        ),
    )

    result = build_domain_run("data-elements", inputs, batch)

    assert len(result.activation.runs) == 3
    assert len(result.activation.evidence) == 1
    assert result.manifest.evidence_count == 1


def test_domain_run_exports_content_inventory_and_full_text(tmp_path: Path) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    inputs = load_input(fixture)
    content_root = tmp_path / "capture"
    text_path = content_root / "content" / "signal-policy.md"
    text_path.parent.mkdir(parents=True)
    text_path.write_text("Policy evidence full text.", encoding="utf-8")
    content = ContentArtifact(
        id="content-signal-policy",
        source_id="official-policy",
        evidence_id="signal-policy",
        title="New data policy published",
        url="https://example.com/policy?utm_source=demo",
        captured_at=inputs.as_of,
        content_type="text/markdown",
        relative_path="content/signal-policy.md",
        content_hash="sha256:content-policy",
        character_count=28,
        status=ContentCaptureStatus.CAPTURED,
    )
    result = build_domain_run(
        "data-elements",
        inputs,
        AcquisitionBatch(
            runs=inputs.acquisition_runs,
            evidence=inputs.evidence,
            contents=(content,),
        ),
    )

    output_dir = tmp_path / "out"
    write_domain_run(result, output_dir, content_root=content_root)

    assert result.manifest.content_count == 1
    assert result.manifest.captured_content_count == 1
    assert (output_dir / "content-inventory.json").is_file()
    assert (output_dir / "content-inventory.md").is_file()
    assert (output_dir / "content" / "signal-policy.md").read_text(encoding="utf-8") == (
        "Policy evidence full text."
    )


def test_cli_domain_run_writes_the_complete_delivery_bundle(tmp_path: Path) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    output_dir = tmp_path / "out"
    environment = os.environ.copy()
    source_dir = str(Path(__file__).parents[1] / "src")
    environment["PYTHONPATH"] = source_dir + os.pathsep + environment.get("PYTHONPATH", "")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "domain_intelligence",
            "--domain",
            "data-elements",
            "--bundle",
            str(fixture),
            "--output-dir",
            str(output_dir),
        ],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    expected = {
        "domain-profile.json",
        "source-map.json",
        "acquisition-plan.json",
        "source-activation.json",
        "knowledge-graph.json",
        "knowledge-graph.md",
        "bootstrap-report.json",
        "bootstrap-report.md",
        "daily-brief.json",
        "daily-brief.md",
        "content-inventory.json",
        "content-inventory.md",
        "run-manifest.json",
    }
    assert {path.name for path in output_dir.iterdir()} == expected
    manifest = json.loads((output_dir / "run-manifest.json").read_text(encoding="utf-8"))
    graph = json.loads((output_dir / "knowledge-graph.json").read_text(encoding="utf-8"))
    assert manifest["source_count"] == 3
    assert graph["domain"] == "data-elements"


def test_cli_domain_run_executes_local_source_snapshots(tmp_path: Path) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    snapshot_dir = tmp_path / "snapshots"
    snapshot_dir.mkdir()
    source_id = payload["attention_graph"]["sources"][0]["id"]
    (snapshot_dir / f"{source_id}.json").write_text(
        json.dumps(payload["evidence"][:1]),
        encoding="utf-8",
    )
    output_dir = tmp_path / "out"
    environment = os.environ.copy()
    source_dir = str(Path(__file__).parents[1] / "src")
    environment["PYTHONPATH"] = source_dir + os.pathsep + environment.get("PYTHONPATH", "")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "domain_intelligence",
            "--domain",
            "data-elements",
            "--bundle",
            str(fixture),
            "--snapshots",
            str(snapshot_dir),
            "--output-dir",
            str(output_dir),
        ],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    activation = json.loads(
        (output_dir / "source-activation.json").read_text(encoding="utf-8"),
    )
    assert len(activation["runs"]) == 3
    assert len(activation["evidence"]) == 1
