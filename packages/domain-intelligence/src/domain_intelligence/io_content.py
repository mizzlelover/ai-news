from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from domain_intelligence.io_json import write_json
from domain_intelligence.models import ContentArtifact, ContentCaptureStatus, ContentInventory


@dataclass(frozen=True, slots=True)
class ContentArchiveMissingError(FileNotFoundError):
    relative_path: str

    def __str__(self) -> str:
        return f"captured content file is missing: {self.relative_path!r}"


@dataclass(frozen=True, slots=True)
class ContentArchivePathError(ValueError):
    relative_path: str

    def __str__(self) -> str:
        return f"content path escapes the capture root: {self.relative_path!r}"


def _content_link(relative_path: str | None, label: str) -> str:
    return f"[{label}]({relative_path})" if relative_path else "-"


def _content_line(item: ContentArtifact) -> str:
    evidence = item.evidence_id or "-"
    return (
        f"| `{item.status.value}` | `{item.source_id}` | `{evidence}` | {item.title} | "
        f"{item.published_at.date().isoformat() if item.published_at else '-'} | "
        f"{item.character_count} | {_content_link(item.relative_path, '全文')} | "
        f"{_content_link(item.raw_relative_path, '原始响应')} |"
    )


def render_content_inventory(inventory: ContentInventory) -> str:
    lines = [
        "# Content Inventory",
        "",
        f"- Generated at: `{inventory.generated_at.isoformat()}`",
        f"- Content artifacts: `{len(inventory.items)}`",
        "",
        "| Status | Source | Evidence | Title | Published | Characters | Text | Raw |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    lines.extend(_content_line(item) for item in inventory.items)
    if not inventory.items:
        lines.append("| `none` | - | - | No content artifacts captured | - | 0 | - | - |")
    return "\n".join(lines) + "\n"


def write_markdown_content(inventory: ContentInventory, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_content_inventory(inventory), encoding="utf-8")


def _safe_content_path(content_root: Path, relative_path: str) -> Path:
    root = content_root.resolve()
    candidate = (content_root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ContentArchivePathError(relative_path) from error
    return candidate


def _validate_content_file(relative_path: str, content_root: Path) -> None:
    source = _safe_content_path(content_root, relative_path)
    if not source.is_file():
        raise ContentArchiveMissingError(relative_path)


def _copy_content_file(relative_path: str, content_root: Path, output_dir: Path) -> None:
    source = _safe_content_path(content_root, relative_path)
    target = output_dir / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def write_content_inventory(
    inventory: ContentInventory,
    output_dir: Path,
    content_root: Path | None = None,
) -> None:
    captured = tuple(
        item for item in inventory.items if item.status is ContentCaptureStatus.CAPTURED
    )
    if not captured:
        write_json(inventory, output_dir / "content-inventory.json")
        write_markdown_content(inventory, output_dir / "content-inventory.md")
        return
    if content_root is None:
        missing_root = "<content_root>"
        raise ContentArchiveMissingError(missing_root)
    for item in captured:
        if item.relative_path is None:
            raise ContentArchiveMissingError(item.id)
        _validate_content_file(item.relative_path, content_root)
        if item.raw_relative_path is not None:
            _validate_content_file(item.raw_relative_path, content_root)
    write_json(inventory, output_dir / "content-inventory.json")
    write_markdown_content(inventory, output_dir / "content-inventory.md")
    for item in captured:
        if item.relative_path is None:
            raise ContentArchiveMissingError(item.id)
        _copy_content_file(item.relative_path, content_root, output_dir)
        if item.raw_relative_path is not None:
            _copy_content_file(item.raw_relative_path, content_root, output_dir)
