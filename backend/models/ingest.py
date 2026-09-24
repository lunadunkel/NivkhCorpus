from typing import Literal

from pydantic import BaseModel, ConfigDict


class IngestConfig(BaseModel):
    """Секция `ingest:` — как готовить json корпуса к загрузке в MongoDB."""
    model_config = ConfigDict(extra="forbid")

    script: Literal["latin", "cyrillic"]
    strip_punct: list[str] = []
    strip_chars: str = ""
    rename: dict[str, str] = {}
    drop_fields: list[str] = []
    spelling: dict[str, str] = {}