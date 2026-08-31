from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Final

from pydantic import TypeAdapter, ValidationError

from domain_intelligence.models import (
    AcquisitionBatch,
    AcquisitionRunStatus,
    EvidenceRecord,
    SnapshotCollectionRequest,
    SourceAcquisitionRun,
    SourceId,
)

EVIDENCE_LIST: Final = TypeAdapter(tuple[EvidenceRecord, ...])


def _failed_run(source_id: SourceId, as_of: datetime, error_code: str) -> SourceAcquisitionRun:
    return SourceAcquisitionRun(
        id=f"snapshot-{source_id}",
        source_id=source_id,
        status=AcquisitionRunStatus.FAILED,
        retrieved_at=as_of,
        error_code=error_code,
    )


def _read_snapshot(path: Path) -> tuple[EvidenceRecord, ...] | str:
    try:
        return EVIDENCE_LIST.validate_json(path.read_bytes())
    except OSError:
        return "SNAPSHOT_UNREADABLE"
    except ValidationError:
        return "SNAPSHOT_INVALID"


def _collect_source(
    request: SnapshotCollectionRequest,
    source_id: SourceId,
) -> tuple[SourceAcquisitionRun, tuple[EvidenceRecord, ...]]:
    path = Path(request.snapshot_dir) / f"{source_id}.json"
    if not path.is_file():
        return _failed_run(source_id, request.as_of, "SNAPSHOT_MISSING"), ()
    parsed = _read_snapshot(path)
    if isinstance(parsed, str):
        return _failed_run(source_id, request.as_of, parsed), ()
    if any(record.source_id != source_id for record in parsed):
        return _failed_run(source_id, request.as_of, "SOURCE_ID_MISMATCH"), ()
    if any(
        record.available_at > record.retrieved_at or record.retrieved_at > request.as_of
        for record in parsed
    ):
        return _failed_run(source_id, request.as_of, "INVALID_EVIDENCE_TIMING"), ()
    status = AcquisitionRunStatus.SUCCEEDED if parsed else AcquisitionRunStatus.EMPTY
    return (
        SourceAcquisitionRun(
            id=f"snapshot-{source_id}",
            source_id=source_id,
            status=status,
            retrieved_at=request.as_of,
            evidence_ids=tuple(record.id for record in parsed),
        ),
        parsed,
    )


def collect_snapshots(request: SnapshotCollectionRequest) -> AcquisitionBatch:
    collected = tuple(
        _collect_source(request, source.id)
        for source in sorted(request.sources, key=lambda item: str(item.id))
    )
    return AcquisitionBatch(
        runs=tuple(run for run, _ in collected),
        evidence=tuple(record for _, records in collected for record in records),
    )
