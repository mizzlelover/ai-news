from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel

from domain_intelligence.models import BootstrapInput


def load_input(path: Path) -> BootstrapInput:
    return BootstrapInput.model_validate_json(path.read_bytes())


def write_json(model: BaseModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2) + "\n", encoding="utf-8")
