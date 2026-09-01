from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from domain_intelligence.io import (
    ContentArchiveMissingError,
    ContentArchivePathError,
    write_content_inventory,
)
from domain_intelligence.models import (
    ContentArtifact,
    ContentCaptureStatus,
    ContentInventory,
)

AS_OF = datetime(2026, 8, 30, 12, tzinfo=UTC)


def _inventory(relative_path: str = "content/article.md") -> ContentInventory:
    return ContentInventory(
        generated_at=AS_OF,
        items=(
            ContentArtifact(
                id="content-source-1",
                source_id="source-1",
                evidence_id="signal-1",
                title="一篇文章",
                url="https://example.test/article",
                captured_at=AS_OF,
                content_type="text/html",
                relative_path=relative_path,
                raw_relative_path="content/article.html",
                content_hash="sha256:test",
                character_count=4,
                status=ContentCaptureStatus.CAPTURED,
            ),
            ContentArtifact(
                id="content-source-2",
                source_id="source-2",
                title="未抓到的文章",
                url="https://example.test/missing",
                captured_at=AS_OF,
                content_type="text/html",
                status=ContentCaptureStatus.FAILED,
                error_code="REQUEST_ERROR",
            ),
        ),
    )


def test_content_archive_copies_text_and_raw_files(tmp_path: Path) -> None:
    capture_root = tmp_path / "capture"
    (capture_root / "content").mkdir(parents=True)
    (capture_root / "content" / "article.md").write_text("全文\n", encoding="utf-8")
    (capture_root / "content" / "article.html").write_text("<p>全文</p>", encoding="utf-8")
    output_dir = tmp_path / "run"

    write_content_inventory(_inventory(), output_dir, capture_root)

    assert (output_dir / "content" / "article.md").read_text(encoding="utf-8") == "全文\n"
    assert (output_dir / "content" / "article.html").read_text(encoding="utf-8") == "<p>全文</p>"
    assert (output_dir / "content-inventory.json").is_file()


@pytest.mark.parametrize(
    ("relative_path", "error_type"),
    [
        ("content/missing.md", ContentArchiveMissingError),
        ("../outside.md", ContentArchivePathError),
    ],
)
def test_content_archive_validates_all_paths_before_writing(
    tmp_path: Path,
    relative_path: str,
    error_type: type[Exception],
) -> None:
    capture_root = tmp_path / "capture"
    (capture_root / "content").mkdir(parents=True)
    (capture_root / "content" / "article.html").write_text("<p>全文</p>", encoding="utf-8")
    output_dir = tmp_path / "run"

    with pytest.raises(error_type):
        write_content_inventory(_inventory(relative_path), output_dir, capture_root)

    assert not (output_dir / "content-inventory.json").exists()
    assert not (output_dir / "content").exists()


def test_content_archive_requires_capture_root_for_captured_items(tmp_path: Path) -> None:
    with pytest.raises(ContentArchiveMissingError):
        write_content_inventory(_inventory(), tmp_path / "run")
