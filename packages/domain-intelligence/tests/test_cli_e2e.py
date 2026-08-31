from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_bootstrap_writes_machine_and_reader_outputs(tmp_path: Path) -> None:
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
    report = json.loads((output_dir / "bootstrap-report.json").read_text(encoding="utf-8"))
    assert report["domain"] == "data-elements"
    assert report["brief"]["stories"]
    assert report["coverage"]["total_elements"] == 3
    assert (output_dir / "bootstrap-report.md").exists()


def test_cli_bootstrap_ingests_evidence_into_the_daily_brief(tmp_path: Path) -> None:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    payload["acquisition_runs"] = [
        {
            "id": "run-policy",
            "source_id": "official-policy",
            "status": "succeeded",
            "retrieved_at": "2026-08-30T08:00:00Z",
            "evidence_ids": ["evidence-policy"],
        },
    ]
    payload["evidence"] = [
        {
            "id": "evidence-policy",
            "source_id": "official-policy",
            "title": "New data policy published",
            "url": "https://example.com/policy/activation",
            "summary": "A policy update entered the public record.",
            "published_at": "2026-08-30T07:00:00Z",
            "available_at": "2026-08-30T07:00:00Z",
            "retrieved_at": "2026-08-30T08:00:00Z",
            "content_hash": "sha256:evidence-policy",
            "topic_ids": ["policy"],
            "element_ids": ["e-policy"],
            "event_type": "policy_change",
            "importance": 0.9,
            "originality": 1.0,
            "confirmed": True,
            "event_id": "event-policy",
        },
    ]
    input_path = tmp_path / "activation-input.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    output_dir = tmp_path / "out"
    environment = os.environ.copy()
    source_dir = str(Path(__file__).parents[1] / "src")
    environment["PYTHONPATH"] = source_dir + os.pathsep + environment.get("PYTHONPATH", "")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "domain_intelligence",
            str(input_path),
            "--output-dir",
            str(output_dir),
        ],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads((output_dir / "bootstrap-report.json").read_text(encoding="utf-8"))
    assert report["activation"]["evidence"][0]["id"] == "evidence-policy"
    assert report["activation"]["signals"][0]["id"] == "evidence-policy"
    assert report["activation"]["knowledge_deltas"][0]["element_ids"] == ["e-policy"]
    assert any(
        story["primary_source_id"] == "official-policy" for story in report["brief"]["stories"]
    )
