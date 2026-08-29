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
