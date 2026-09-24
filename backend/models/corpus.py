from pydantic import BaseModel, Field, model_validator

from backend.models.grammar import GrammarBlock, Layout
from backend.models.page import Assets, LanguageOption, PageMeta, Vocabulary
from backend.models.search import SearchConfig
from backend.models.ingest import IngestConfig


class CorpusConfig(BaseModel):
    """Один корпус целиком, как он описан в YAML.

    Модель хранит форму конфига и проверяет его на согласованность при загрузке.
    """

    id: str
    enabled: bool = True
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