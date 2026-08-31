from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from domain_intelligence.models.core import StrictModel
from domain_intelligence.models.types import SourceId


class ContentCaptureStatus(StrEnum):
    CAPTURED = "captured"
    FAILED = "failed"
    BLOCKED = "blocked"


class ContentArtifact(StrictModel):
    id: str = Field(min_length=1)
    source_id: SourceId
    evidence_id: str | None = Field(default=None, min_length=1)
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    published_at: datetime | None = None
    captured_at: datetime
    content_type: str = Field(min_length=1)
    relative_path: str | None = Field(default=None, min_length=1)
    raw_relative_path: str | None = Field(default=None, min_length=1)
    content_hash: str | None = Field(default=None, min_length=1)
    character_count: int = Field(default=0, ge=0)
    status: ContentCaptureStatus
    error_code: str | None = Field(default=None, min_length=1)


class ContentInventory(StrictModel):
    generated_at: datetime
    items: tuple[ContentArtifact, ...]
