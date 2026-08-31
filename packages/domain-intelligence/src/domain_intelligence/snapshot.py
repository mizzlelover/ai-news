from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Final

from pydantic import TypeAdapter, ValidationError

from domain_intelligence.models import (
    AcquisitionBatch,
    AcquisitionRunStatus,
    ContentArtifact,
    ContentCaptureStatus,
    ContentInventory,
    EvidenceRecord,
    SnapshotCollectionRequest,
    SourceAcquisitionRun,
    SourceId,
    SourceProfile,
)

EVIDENCE_LIST: Final = TypeAdapter(tuple[EvidenceRecord, ...])


class SnapshotContentInventoryError(ValueError):
    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"invalid content inventory {path}: {reason}")


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


def _load_content_inventory(
    snapshot_dir: Path,
    sources: tuple[SourceProfile, ...],
    as_of: datetime,
) -> ContentInventory:
    path = snapshot_dir / "content-inventory.json"
    if not path.is_file():
        return ContentInventory(generated_at=as_of, items=())
    try:
        inventory = ContentInventory.model_validate_json(path.read_bytes())
    except (OSError, ValidationError) as error:
        raise SnapshotContentInventoryError(path, type(error).__name__) from error
    source_ids = {str(source.id) for source in sources}
    root = snapshot_dir.resolve()
    for item in inventory.items:
        if str(item.source_id) not in source_ids:
            raise SnapshotContentInventoryError(path, f"unknown source {item.source_id}")
        _validate_content_item(snapshot_dir, root, path, item)
    return inventory


def _validate_content_item(
    snapshot_dir: Path,
    root: Path,
    inventory_path: Path,
    item: ContentArtifact,
) -> None:
    if item.status is not ContentCaptureStatus.CAPTURED:
        return
    if item.relative_path is None:
        raise SnapshotContentInventoryError(
            inventory_path,
            f"captured item {item.id} has no text path",
        )
    for relative_path in (item.relative_path, item.raw_relative_path):
        if relative_path is None:
            continue
        candidate = (snapshot_dir / relative_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as error:
            reason = f"path escapes root: {relative_path}"
            raise SnapshotContentInventoryError(inventory_path, reason) from error
        if not candidate.is_file():
            raise SnapshotContentInventoryError(inventory_path, f"missing file: {relative_path}")


def collect_snapshots(request: SnapshotCollectionRequest) -> AcquisitionBatch:
    snapshot_dir = Path(request.snapshot_dir)
    inventory = _load_content_inventory(snapshot_dir, request.sources, request.as_of)
    collected = tuple(
        _collect_source(request, source.id)
        for source in sorted(request.sources, key=lambda item: str(item.id))
    )
    return AcquisitionBatch(
        runs=tuple(run for run, _ in collected),
        evidence=tuple(record for _, records in collected for record in records),
        contents=inventory.items,
    )
