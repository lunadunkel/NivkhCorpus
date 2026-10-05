from pydantic import BaseModel, Field, field_validator, model_validator

from backend.models.grammar import GrammarBlock, Layout
from backend.models.page import Assets, LanguageOption, PageMeta, Vocabulary
from backend.models.search import SearchConfig
from backend.models.ingest import IngestConfig


DEFAULT_INDEXED_FIELDS = [
    "tokens.token",
    "tokens.lemma",
    "tokens.tagsets.POS",
    "tokens.tagsets.Case",
    "tokens.tagsets.Tense",
    "tokens.tagsets.Person[word]",
    "tokens.tagsets.Number[word]",
]

class CorpusConfig(BaseModel):
    """Один корпус целиком, как он описан в YAML.

    Модель хранит форму конфига и проверяет его на согласованность при загрузке.
    """

    id: str
    languages: list[LanguageOption]
    search: SearchConfig = Field(default_factory=SearchConfig)
    keyboard: list[list[str]] = []
    assets: Assets = Field(default_factory=Assets)
    pages: dict[str, PageMeta] = {}
    layout: Layout = Field(default_factory=Layout)
    grammar: list[GrammarBlock] = []
    dictionary: list[Vocabulary] = []
    alphabet_order: list[str] = []
    alphabet_order: list[str] = []
    ingest: IngestConfig | None = None
    indexes: list[str] = Field(default_factory=lambda: list(DEFAULT_INDEXED_FIELDS))


    @field_validator("indexes")
    @classmethod
    def _clean_indexes(cls, fields: list[str]) -> list[str]:
        cleaned = [f.strip() for f in fields]
        if not all(cleaned):
            raise ValueError("indexes: empty field name")
        return list(dict.fromkeys(cleaned))

    @model_validator(mode="after")
    def _layout_validator(self) -> "CorpusConfig":
        """Каждый блок грамматики стоит в layout ровно один раз."""
        known = set()
        for block in self.grammar:
            known.add(block.id)

        placed = set()
        for column in self.layout.columns:
            for block_id in column:
                if block_id not in known:
                    raise ValueError(
                        f"{self.id}: в layout есть блок {block_id!r}, "
                        f"которого нет в grammar"
                    )
                if block_id in placed:
                    raise ValueError(
                        f"{self.id}: блок {block_id!r} стоит в layout дважды"
                    )
                placed.add(block_id)

        missing = known - placed
        if missing:
            raise ValueError(
                f"{self.id}: блоки {sorted(missing)} не стоят ни в одной "
                f"колонке layout"
            )
        return self

    @model_validator(mode="after")
    def _checkboxes_are_unique(self) -> "CorpusConfig":
        """Ни одна пара имя=значение не встречается в двух блоках сразу."""
        seen = set()
        duplicates = set()
        for block in self.grammar:
            for name, values in block.fields().items():
                for value in values:
                    checkbox = f"{name}={value}"
                    if checkbox in seen:
                        duplicates.add(checkbox)
                    seen.add(checkbox)

        if duplicates:
            raise ValueError(
                f"{self.id}: повторяющиеся чекбоксы {sorted(duplicates)}"
            )
        return self