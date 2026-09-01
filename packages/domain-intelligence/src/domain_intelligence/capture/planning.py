from __future__ import annotations

from datetime import datetime
from typing import assert_never

from domain_intelligence.capture.archive import failure
from domain_intelligence.capture.contracts import CaptureOutcome, CaptureTarget
from domain_intelligence.models import (
    AcquisitionMethod,
    AcquisitionRunStatus,
    ContentCaptureStatus,
    DailySignal,
    EvidenceRecord,
    SourceAcquisitionRun,
    SourceProfile,
)


def source_blocker(source: SourceProfile) -> str | None:
    if not source.approved:
        return "SOURCE_NOT_APPROVED"
    if not source.acquisition.stable:
        return "ACQUISITION_NOT_STABLE"
    if not source.acquisition.endpoint:
        return "NO_PUBLIC_ENDPOINT"
    match source.acquisition.method:
        case (
            AcquisitionMethod.RSS
            | AcquisitionMethod.ATOM
            | AcquisitionMethod.JSON
            | AcquisitionMethod.SITEMAP
            | AcquisitionMethod.STATIC_HTML
            | AcquisitionMethod.API
            | AcquisitionMethod.OPML
        ):
            return None
        case AcquisitionMethod.BROWSER:
            return "BROWSER_ADAPTER_REQUIRED"
        case AcquisitionMethod.MANUAL | AcquisitionMethod.UNKNOWN:
            return "ACQUISITION_METHOD_UNSUPPORTED"
        case unreachable:
            assert_never(unreachable)


def targets_for_source(
    source: SourceProfile,
    signals: tuple[DailySignal, ...],
    evidence_by_id: dict[str, EvidenceRecord],
) -> tuple[CaptureTarget, ...]:
    endpoint = source.acquisition.endpoint
    if endpoint is None:
        return ()
    targets = [CaptureTarget(source, endpoint, None, None)]
    for signal in signals:
        target = CaptureTarget(source, signal.url, signal, evidence_by_id.get(str(signal.id)))
        if signal.url == endpoint:
            targets[0] = target
        else:
            targets.append(target)
    return tuple(targets)


def blocked_outcome(
    source: SourceProfile,
    error_code: str,
    as_of: datetime,
) -> CaptureOutcome | None:
    endpoint = source.acquisition.endpoint
    if endpoint is None:
        return None
    target = CaptureTarget(source, endpoint, None, None)
    return failure(target, as_of, ContentCaptureStatus.BLOCKED, error_code)


def source_run(
    source: SourceProfile,
    outcomes: tuple[CaptureOutcome, ...],
    as_of: datetime,
) -> SourceAcquisitionRun:
    evidence_ids = tuple(
        outcome.evidence.id for outcome in outcomes if outcome.evidence is not None
    )
    captured = any(outcome.artifact.status is ContentCaptureStatus.CAPTURED for outcome in outcomes)
    if evidence_ids:
        status = AcquisitionRunStatus.SUCCEEDED
        error_code = None
    elif captured:
        status = AcquisitionRunStatus.EMPTY
        error_code = next(
            (
                outcome.discovery_error_code
                for outcome in outcomes
                if outcome.discovery_error_code is not None
            ),
            None,
        )
    else:
        status = AcquisitionRunStatus.FAILED
        error_code = next(
            (
                outcome.artifact.error_code
                for outcome in outcomes
                if outcome.artifact.error_code is not None
            ),
            "NO_CAPTURED_CONTENT",
        )
    return SourceAcquisitionRun(
        id=f"live-{source.id}",
        source_id=source.id,
        status=status,
        retrieved_at=as_of,
        evidence_ids=evidence_ids,
        error_code=error_code,
    )
