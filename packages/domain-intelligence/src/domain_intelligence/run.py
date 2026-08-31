from __future__ import annotations

import hashlib
from dataclasses import dataclass

from domain_intelligence.acquisition import build_acquisition_plan
from domain_intelligence.models import (
    AcquisitionBatch,
    AcquisitionPlanStatus,
    BootstrapInput,
    ContentCaptureStatus,
    ContentInventory,
    DomainRunManifest,
    DomainRunResult,
)
from domain_intelligence.pipeline import build_bootstrap_report


@dataclass(frozen=True, slots=True)
class DomainMismatchError(ValueError):
    requested_domain: str
    seed_domain: str

    def _message(self) -> str:
        return (
            f"requested domain {self.requested_domain!r} does not match "
            f"seed domain {self.seed_domain!r}"
        )

    __str__ = _message


def build_domain_run(
    domain: str,
    inputs: BootstrapInput,
    acquisition: AcquisitionBatch | None = None,
    input_mode: str = "domain_seed_bundle",
) -> DomainRunResult:
    requested_domain = domain.strip()
    if requested_domain != inputs.profile.domain:
        raise DomainMismatchError(requested_domain, inputs.profile.domain)
    if acquisition is not None:
        inputs = inputs.model_copy(
            update={"acquisition_runs": acquisition.runs, "evidence": acquisition.evidence},
        )
    report = build_bootstrap_report(inputs)
    plan = build_acquisition_plan(inputs.attention_graph.sources, inputs.as_of)
    ready_count = sum(item.status is AcquisitionPlanStatus.READY for item in plan.items)
    blocked_count = len(plan.items) - ready_count
    contents = acquisition.contents if acquisition is not None else ()
    content_inventory = ContentInventory(generated_at=inputs.as_of, items=contents)
    captured_content_count = sum(item.status is ContentCaptureStatus.CAPTURED for item in contents)
    run_id = hashlib.sha256(
        f"{requested_domain}|{inputs.as_of.isoformat()}".encode(),
    ).hexdigest()[:16]
    manifest = DomainRunManifest(
        run_id=run_id,
        domain=requested_domain,
        generated_at=inputs.as_of,
        input_mode=input_mode,
        source_count=len(inputs.attention_graph.sources),
        ready_source_count=ready_count,
        blocked_source_count=blocked_count,
        evidence_count=len(report.activation.evidence),
        content_count=len(contents),
        captured_content_count=captured_content_count,
        signal_count=len(report.signals),
        story_count=len(report.brief.stories),
        artifacts=(
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
            *(("content/",) if captured_content_count else ()),
            "run-manifest.json",
        ),
    )
    return DomainRunResult(
        manifest=manifest,
        profile=inputs.profile,
        source_map=inputs.attention_graph,
        plan=plan,
        activation=report.activation,
        knowledge_graph=report.knowledge_graph,
        report=report,
        content_inventory=content_inventory,
    )
