from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Final, assert_never

from domain_intelligence.models.activation import (
    AcquisitionRunStatus,
    ActivationInput,
    ActivationReport,
    ActivationStatus,
    EvidenceRecord,
    KnowledgeChangeType,
    KnowledgeDomainDelta,
    SourceAcquisitionRun,
    SourceActivation,
)
from domain_intelligence.models.core import SourceProfile
from domain_intelligence.models.daily import DailySignal
from domain_intelligence.models.types import AcquisitionMethod, SourceId

BLOCKED_ACQUISITION_METHODS: Final = frozenset(
    {AcquisitionMethod.MANUAL, AcquisitionMethod.UNKNOWN},
)


@dataclass(frozen=True, slots=True)
class UnknownActivationSourceError(LookupError):
    source_id: SourceId

    def _message(self) -> str:
        return f"activation source {self.source_id!s} is not present in the source graph"

    __str__ = _message


@dataclass(frozen=True, slots=True)
class UnknownActivationEvidenceError(LookupError):
    evidence_id: str

    def _message(self) -> str:
        return f"activation run references unknown evidence {self.evidence_id!r}"

    __str__ = _message


@dataclass(frozen=True, slots=True)
class DuplicateActivationEvidenceError(ValueError):
    evidence_id: str

    def _message(self) -> str:
        return f"activation evidence id {self.evidence_id!r} is duplicated"

    __str__ = _message


@dataclass(frozen=True, slots=True)
class DuplicateActivationRunError(ValueError):
    source_id: SourceId

    def _message(self) -> str:
        return f"activation run for source {self.source_id!s} is duplicated"

    __str__ = _message


@dataclass(frozen=True, slots=True)
class InvalidEvidenceTimingError(ValueError):
    evidence_id: str
    reason: str

    def _message(self) -> str:
        return f"invalid timing for activation evidence {self.evidence_id!r}: {self.reason}"

    __str__ = _message


def _source_is_ready(source: SourceProfile) -> bool:
    return (
        source.approved
        and source.acquisition.stable
        and bool(source.acquisition.endpoint)
        and source.acquisition.method not in BLOCKED_ACQUISITION_METHODS
    )


def _status_for(
    source: SourceProfile,
    run: SourceAcquisitionRun | None,
    evidence_count: int,
) -> ActivationStatus:
    if not _source_is_ready(source):
        return ActivationStatus.BLOCKED
    if run is None:
        return ActivationStatus.OBSERVED if evidence_count else ActivationStatus.READY
    match run.status:
        case AcquisitionRunStatus.SUCCEEDED:
            return ActivationStatus.OBSERVED if evidence_count else ActivationStatus.EMPTY
        case AcquisitionRunStatus.EMPTY:
            return ActivationStatus.EMPTY
        case AcquisitionRunStatus.FAILED:
            return ActivationStatus.FAILED
        case unreachable:
            assert_never(unreachable)


def _collect_evidence(
    inputs: ActivationInput,
    sources: dict[str, SourceProfile],
) -> dict[str, EvidenceRecord]:
    evidence: dict[str, EvidenceRecord] = {}
    for record in inputs.evidence:
        if str(record.source_id) not in sources:
            raise UnknownActivationSourceError(record.source_id)
        if record.id in evidence:
            raise DuplicateActivationEvidenceError(record.id)
        if record.available_at > record.retrieved_at:
            raise InvalidEvidenceTimingError(record.id, "available_at is after retrieved_at")
        if record.retrieved_at > inputs.as_of:
            raise InvalidEvidenceTimingError(record.id, "retrieved_at is after as_of")
        evidence[record.id] = record
    return evidence


def _collect_runs(
    inputs: ActivationInput,
    sources: dict[str, SourceProfile],
    evidence: dict[str, EvidenceRecord],
) -> dict[str, SourceAcquisitionRun]:
    runs: dict[str, SourceAcquisitionRun] = {}
    for run in inputs.runs:
        source_key = str(run.source_id)
        if source_key not in sources:
            raise UnknownActivationSourceError(run.source_id)
        if source_key in runs:
            raise DuplicateActivationRunError(run.source_id)
        for evidence_id in run.evidence_ids:
            if evidence_id not in evidence:
                raise UnknownActivationEvidenceError(evidence_id)
        runs[source_key] = run
    return runs


def _validate_input(
    inputs: ActivationInput,
) -> tuple[dict[str, SourceProfile], dict[str, EvidenceRecord], dict[str, SourceAcquisitionRun]]:
    sources = {str(source.id): source for source in inputs.sources}
    evidence = _collect_evidence(inputs, sources)
    runs = _collect_runs(inputs, sources, evidence)
    return sources, evidence, runs


def _signal(record: EvidenceRecord) -> DailySignal:
    return DailySignal(
        id=record.id,
        source_id=record.source_id,
        title=record.title,
        url=record.url,
        published_at=record.published_at,
        available_at=record.available_at,
        topic_ids=record.topic_ids,
        event_type=record.event_type,
        importance=record.importance,
        summary=record.summary,
        originality=record.originality,
        confirmed=record.confirmed,
        event_id=record.event_id,
    )


def build_activation_report(inputs: ActivationInput) -> ActivationReport:
    sources, evidence_by_id, runs = _validate_input(inputs)
    window_start = inputs.as_of - timedelta(hours=inputs.window_hours)
    evidence = tuple(sorted(evidence_by_id.values(), key=lambda item: (item.available_at, item.id)))
    evidence_by_source: dict[str, list[EvidenceRecord]] = {}
    for record in evidence:
        evidence_by_source.setdefault(str(record.source_id), []).append(record)

    source_statuses = tuple(
        SourceActivation(
            source_id=source.id,
            status=_status_for(
                source,
                runs.get(str(source.id)),
                len(evidence_by_source.get(str(source.id), [])),
            ),
            last_run_at=(runs[str(source.id)].retrieved_at if str(source.id) in runs else None),
            evidence_count=len(evidence_by_source.get(str(source.id), [])),
        )
        for source in sorted(sources.values(), key=lambda item: str(item.id))
    )
    signals = tuple(
        _signal(record)
        for record in evidence
        if window_start <= record.available_at <= inputs.as_of
    )
    knowledge_deltas = tuple(
        KnowledgeDomainDelta(
            evidence_id=record.id,
            source_id=record.source_id,
            change_type=KnowledgeChangeType.NEW_EVIDENCE,
            topic_ids=record.topic_ids,
            element_ids=record.element_ids,
        )
        for record in evidence
    )
    return ActivationReport(
        generated_at=inputs.as_of,
        window_start=window_start,
        source_statuses=source_statuses,
        runs=tuple(sorted(runs.values(), key=lambda item: str(item.id))),
        evidence=evidence,
        signals=signals,
        knowledge_deltas=knowledge_deltas,
    )
