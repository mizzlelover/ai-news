from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import stat
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from domain_intelligence.capture.contracts import CaptureOutcome, CaptureTarget
from domain_intelligence.models import (
    ContentArtifact,
    ContentCaptureStatus,
    ContentInventory,
    SourceProfile,
)

SAFE_SOURCE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


@dataclass(frozen=True, slots=True)
class UnsafeSourceIdError(ValueError):
    source_id: str


@dataclass(frozen=True, slots=True)
class UnsafeCapturePathError(ValueError):
    relative_path: str


def content_id(target: CaptureTarget) -> str:
    signal_id = target.signal.id if target.signal is not None else ""
    feed_identity = target.feed_item.identity if target.feed_item is not None else ""
    digest = hashlib.sha256(
        f"{target.source.id}|{target.url}|{signal_id}|{feed_identity}".encode(),
    ).hexdigest()[:16]
    source = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(target.source.id)).strip("-") or "source"
    return f"content-{source}-{digest}"


def raw_extension(content_type: str) -> str:
    normalized_type = content_type.casefold()
    if "pdf" in normalized_type:
        return ".pdf"
    if "json" in normalized_type:
        return ".json"
    if "xml" in normalized_type or "rss" in normalized_type or "atom" in normalized_type:
        return ".xml"
    if "html" in normalized_type:
        return ".html"
    return ".txt"


def normalize_content_text(text: str) -> str:
    return text.rstrip("\r\n") + "\n"


def _open_directory(path: Path, relative_path: str) -> int:
    if path.is_symlink():
        raise UnsafeCapturePathError(relative_path)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise UnsafeCapturePathError(relative_path) from error
    try:
        is_directory = stat.S_ISDIR(os.fstat(descriptor).st_mode)
    except OSError:
        os.close(descriptor)
        raise
    if not is_directory:
        os.close(descriptor)
        raise UnsafeCapturePathError(relative_path)
    return descriptor


def _open_directory_at(parent: int, name: str, relative_path: str) -> int:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=parent)
    except OSError as error:
        raise UnsafeCapturePathError(relative_path) from error
    try:
        is_directory = stat.S_ISDIR(os.fstat(descriptor).st_mode)
    except OSError:
        os.close(descriptor)
        raise
    if not is_directory:
        os.close(descriptor)
        raise UnsafeCapturePathError(relative_path)
    return descriptor


def _atomic_write_at(directory: int, filename: str, payload: bytes) -> None:
    if not filename or Path(filename).name != filename or filename in {".", ".."}:
        raise UnsafeCapturePathError(filename)
    try:
        existing = os.stat(filename, dir_fd=directory, follow_symlinks=False)
    except FileNotFoundError:
        existing = None
    if existing is not None and stat.S_ISLNK(existing.st_mode):
        raise UnsafeCapturePathError(filename)

    temporary_name = f".{filename}.{secrets.token_hex(8)}.tmp"
    descriptor: int | None = None
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(temporary_name, flags, 0o600, dir_fd=directory)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(
            temporary_name,
            filename,
            src_dir_fd=directory,
            dst_dir_fd=directory,
        )
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        with suppress(OSError):
            os.unlink(temporary_name, dir_fd=directory)
        raise


def source_snapshot_path(capture_root: Path, source_id: str) -> Path:
    value = str(source_id)
    if not SAFE_SOURCE_ID_PATTERN.fullmatch(value):
        raise UnsafeSourceIdError(value)
    root = capture_root.resolve()
    candidate = (root / f"{value}.json").resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise UnsafeSourceIdError(value) from error
    return candidate


def failure(
    target: CaptureTarget,
    as_of: datetime,
    status: ContentCaptureStatus,
    error_code: str,
    content_type: str = "application/octet-stream",
) -> CaptureOutcome:
    title = (
        target.feed_item.title
        if target.feed_item is not None
        else target.signal.title
        if target.signal is not None
        else target.source.name
    )
    artifact = ContentArtifact(
        id=content_id(target),
        source_id=target.source.id,
        title=title,
        url=target.url,
        captured_at=as_of,
        content_type=content_type,
        status=status,
        error_code=error_code,
    )
    return CaptureOutcome(artifact=artifact, evidence=None)


def write_capture_files(
    capture_root: Path,
    target: CaptureTarget,
    body: bytes,
    text: str,
    content_type: str,
) -> tuple[str, str]:
    current_id = content_id(target)
    text_relative_path = f"content/{current_id}.md"
    raw_relative_path = f"content/{current_id}{raw_extension(content_type)}"
    root_descriptor = _open_directory(capture_root, ".")
    try:
        with suppress(FileExistsError):
            os.mkdir("content", 0o755, dir_fd=root_descriptor)
        content_descriptor = _open_directory_at(root_descriptor, "content", "content")
        try:
            _atomic_write_at(
                content_descriptor,
                f"{current_id}.md",
                normalize_content_text(text).encode("utf-8"),
            )
            _atomic_write_at(
                content_descriptor,
                f"{current_id}{raw_extension(content_type)}",
                body,
            )
        finally:
            os.close(content_descriptor)
    finally:
        os.close(root_descriptor)
    return text_relative_path, raw_relative_path


def write_source_snapshots(
    capture_root: Path,
    sources: tuple[SourceProfile, ...],
    outcomes_by_source: dict[str, tuple[CaptureOutcome, ...]],
) -> None:
    root_descriptor = _open_directory(capture_root, ".")
    try:
        for source in sources:
            source_id = str(source.id)
            source_snapshot_path(capture_root, source_id)
            evidence = tuple(
                outcome.evidence
                for outcome in outcomes_by_source.get(source_id, ())
                if outcome.evidence is not None
            )
            payload = [record.model_dump(mode="json") for record in evidence]
            _atomic_write_at(
                root_descriptor,
                f"{source_id}.json",
                (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
            )
    finally:
        os.close(root_descriptor)


def write_capture_inventory(
    capture_root: Path,
    as_of: datetime,
    artifacts: tuple[ContentArtifact, ...],
) -> None:
    inventory = ContentInventory(generated_at=as_of, items=artifacts)
    root_descriptor = _open_directory(capture_root, ".")
    try:
        _atomic_write_at(
            root_descriptor,
            "content-inventory.json",
            (inventory.model_dump_json(indent=2) + "\n").encode("utf-8"),
        )
    finally:
        os.close(root_descriptor)
