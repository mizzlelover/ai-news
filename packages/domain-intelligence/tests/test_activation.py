from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from domain_intelligence.activation import (
    InvalidEvidenceTimingError,
    UnknownActivationSourceError,
    build_activation_report,
)
from domain_intelligence.models import (
    AcquisitionCapability,
    AcquisitionMethod,
    AcquisitionRunStatus,
    ActivationInput,
    ActivationStatus,
    EvidenceRecord,
    KnowledgeChangeType,
    SourceAcquisitionRun,
    SourceProfile,
    SourceRole,
)

AS_OF = datetime(2026, 8, 31, 8, tzinfo=UTC)


def source(source_id: str) -> SourceProfile:
    return SourceProfile(
        id=source_id,
        name=source_id,
        role=SourceRole.OFFICIAL_PRIMARY,
        topic_ids=("policy",),
        element_ids=("e-policy",),
        acquisition=AcquisitionCapability(
            method=AcquisitionMethod.RSS,
            endpoint=f"https://example.com/{source_id}.xml",
            stable=True,
        ),
    )


def test_activation_turns_evidence_into_signal_and_domain_delta() -> None:
    evidence = EvidenceRecord(
        id="evidence-1",
        source_id="official-policy",
        title="A policy change was published",
        url="https://example.com/policy/1",
        summary="The official policy changes the implementation boundary.",
        published_at=AS_OF - timedelta(hours=2),
        available_at=AS_OF - timedelta(hours=2),
        retrieved_at=AS_OF,
        content_hash="sha256:evidence-1",
        topic_ids=("policy",),
        element_ids=("e-policy",),
        event_type="policy_change",
        importance=0.9,
        originality=1.0,
        confirmed=True,
        event_id="event-policy",
    )

    result = build_activation_report(
        ActivationInput(
            sources=(source("official-policy"),),
            runs=(
                SourceAcquisitionRun(
                    id="run-1",
                    source_id="official-policy",
                    status=AcquisitionRunStatus.SUCCEEDED,
                    retrieved_at=AS_OF,
                    evidence_ids=("evidence-1",),
                ),
            ),
            evidence=(evidence,),
            as_of=AS_OF,
            window_hours=24,
        ),
    )

    assert result.source_statuses[0].status is ActivationStatus.OBSERVED
    assert result.source_statuses[0].evidence_count == 1
    assert result.signals[0].id == "evidence-1"
    assert result.signals[0].event_id == "event-policy"
    assert result.knowledge_deltas[0].change_type is KnowledgeChangeType.NEW_EVIDENCE
    assert result.knowledge_deltas[0].element_ids == ("e-policy",)


def test_activation_distinguishes_failed_empty_and_unrun_sources() -> None:
    result = build_activation_report(
        ActivationInput(
            sources=(source("failed"), source("empty"), source("unrun")),
            runs=(
                SourceAcquisitionRun(
                    id="run-failed",
                    source_id="failed",
                    status=AcquisitionRunStatus.FAILED,
                    retrieved_at=AS_OF,
                    error_code="timeout",
                ),
                SourceAcquisitionRun(
                    id="run-empty",
                    source_id="empty",
                    status=AcquisitionRunStatus.EMPTY,
                    retrieved_at=AS_OF,
                ),
            ),
            as_of=AS_OF,
            window_hours=24,
        ),
    )

    statuses = {item.source_id: item.status for item in result.source_statuses}
    assert statuses == {
        "empty": ActivationStatus.EMPTY,
        "failed": ActivationStatus.FAILED,
        "unrun": ActivationStatus.READY,
    }


def test_activation_rejects_evidence_from_unknown_source() -> None:
    evidence = EvidenceRecord(
        id="evidence-unknown",
        source_id="not-in-graph",
        title="Unknown source evidence",
        url="https://example.com/unknown",
        published_at=AS_OF,
        available_at=AS_OF,
        retrieved_at=AS_OF,
        content_hash="sha256:unknown",
    )

    with pytest.raises(UnknownActivationSourceError):
        build_activation_report(
            ActivationInput(
                sources=(source("known"),),
                evidence=(evidence,),
                as_of=AS_OF,
            ),
        )


def test_activation_rejects_evidence_retrieved_after_report_time() -> None:
    evidence = EvidenceRecord(
        id="evidence-future",
        source_id="known",
        title="Future evidence",
        url="https://example.com/future",
        published_at=AS_OF,
        available_at=AS_OF,
        retrieved_at=AS_OF + timedelta(hours=1),
        content_hash="sha256:future",
    )

    with pytest.raises(InvalidEvidenceTimingError):
        build_activation_report(
            ActivationInput(
                sources=(source("known"),),
                evidence=(evidence,),
                as_of=AS_OF,
            ),
        )
