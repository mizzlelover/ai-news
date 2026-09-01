from __future__ import annotations

import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

from domain_intelligence import io
from domain_intelligence.models import (
    AcquisitionRunStatus,
    ContentArtifact,
    ContentCaptureStatus,
    ContentInventory,
    SourceAcquisitionRun,
)
from domain_intelligence.public_capture import capture_public_sources
from domain_intelligence.run import build_domain_run


def test_public_facade_imports_and_signatures_are_stable() -> None:
    expected = {
        capture_public_sources: (
            "(inputs: 'BootstrapInput', capture_root: 'Path', *, "
            "max_body_bytes: 'int' = 12000000) -> 'AcquisitionBatch'"
        ),
        io.load_input: "(path: 'Path') -> 'BootstrapInput'",
        io.write_json: "(model: 'BaseModel', path: 'Path') -> 'None'",
        io.write_markdown: "(report: 'BootstrapReport', path: 'Path') -> 'None'",
        io.write_domain_run: (
            "(result: 'DomainRunResult', output_dir: 'Path', "
            "content_root: 'Path | None' = None) -> 'None'"
        ),
    }

    for function, signature in expected.items():
        assert str(inspect.signature(function)) == signature


def test_serialized_model_field_order_and_enum_values_are_stable() -> None:
    assert tuple(ContentArtifact.model_fields) == (
        "id",
        "source_id",
        "evidence_id",
        "title",
        "url",
        "published_at",
        "captured_at",
        "content_type",
        "relative_path",
        "raw_relative_path",
        "content_hash",
        "character_count",
        "status",
        "error_code",
    )
    assert tuple(ContentInventory.model_fields) == ("generated_at", "items")
    assert tuple(SourceAcquisitionRun.model_fields) == (
        "id",
        "source_id",
        "status",
        "retrieved_at",
        "evidence_ids",
        "error_code",
    )
    assert tuple(ContentCaptureStatus) == (
        ContentCaptureStatus.CAPTURED,
        ContentCaptureStatus.FAILED,
        ContentCaptureStatus.BLOCKED,
    )
    assert tuple(AcquisitionRunStatus) == (
        AcquisitionRunStatus.SUCCEEDED,
        AcquisitionRunStatus.EMPTY,
        AcquisitionRunStatus.FAILED,
    )


def test_domain_run_manifest_artifact_names_are_stable() -> None:
    fixture = Path(__file__).parents[1] / "examples" / "data-elements.json"
    inputs = io.load_input(fixture)

    result = build_domain_run("data-elements", inputs)

    assert result.manifest.artifacts == (
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
    )


def test_strict_public_models_reject_unknown_serialized_fields() -> None:
    with pytest.raises(ValidationError):
        ContentInventory.model_validate(
            {"generated_at": "2026-08-30T00:00:00Z", "items": [], "extra": 1}
        )
