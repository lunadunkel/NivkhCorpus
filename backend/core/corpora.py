"""Модели pydantic с настройками корпусов"""

from pydantic import BaseModel, Field, model_validator


class LanguageOption(BaseModel):
    """Опция <select> рядом со строкой поиска."""
    value: str
    label: str
    selected: bool = False

class Assets(BaseModel):
    """Корпусные css/js поверх общих."""
    styles: list[str] = []
    scripts: list[str] = []

class PageMeta(BaseModel):
    """Meta-информация всех страниц"""
    template: str
    title: str
    description: str = ""
    og_title: str | None = None
    og_description: str | None = None
    og_image_alt: str = ""
    og_type: str = "website"
    canonical: str = ""
    noindex: bool = False
    styles: list[str] = []

    @model_validator(mode="after")
    def _fill_og(self) -> "PageMeta":
        if self.og_title is None:
            self.og_title = self.title
        if self.og_description is None:
            self.og_description = self.description
        return self


class GrammarValue(BaseModel):
    """Один чекбокс внутри блока."""
    value: str
    label: str
    tooltip: str = ""
    field: str | None = None   # переопределяет name (бывший MISC)
    array: bool = True         # False -> name без квадратных скобок
    show: bool = True

    def name(self, block_id: str) -> str:
        field = self.field or block_id
        return f"{field}[]" if self.array else field


class GrammarBlock(BaseModel):
    id: str
    label: str
    tooltip: str = ""
    html_id: str | None = None
    select_all: bool = True
    show: bool = True
    values: list[GrammarValue]

    @property
    def visible_values(self) -> list[GrammarValue]:
        return [v for v in self.values if v.show]

class Layout(BaseModel):
    columns: list[list[str]] = []

class Vocabulary(BaseModel):
    letter: str
    example: str

class CorpusConfig(BaseModel):
    """Базовый корпусный конфиг"""
    id: str
    enabled: bool = True
    languages: list[LanguageOption]
    keyboard: list[list[str]] = []
    assets: Assets = Field(default_factory=Assets)
    pages: dict[str, PageMeta] = {}
    layout: Layout = Field(default_factory=Layout)
    grammar: list[GrammarBlock] = []
    dictionary: list[Vocabulary] = []
    alphabet_order: list[str] = []

    @model_validator(mode="after")
    def _check_layout(self) -> "CorpusConfig":
        known = {b.id for b in self.grammar}
        placed: set[str] = set()

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
                f"{self.id}: блоки {sorted(missing)} не попали ни в одну "
                f"колонку layout — они не отрисуются"
            )

        # Ключ — то, что реально уйдёт в форму: name + value. Два значения
        # с одинаковым value, но разными field (clobj/clpos) — не дубль.
        names = [
            f"{v.name(b.id)}={v.value}" for b in self.grammar for v in b.values
        ]
        dupes = {n for n in names if names.count(n) > 1}
        if dupes:
            raise ValueError(f"{self.id}: повторяющиеся чекбоксы {sorted(dupes)}")

        return self

    @property
    def blocks(self) -> dict[str, GrammarBlock]:
        return {b.id: b for b in self.grammar}

    def columns(self) -> list[list[GrammarBlock]]:
        """Блоки, разложенные по колонкам модала."""
        by_id = self.blocks
        return [
            [by_id[bid] for bid in column if by_id[bid].show]
            for column in self.layout.columns
        ]

    def public_dict(self) -> dict:
        """То, что уезжает в <script id="corpus-config"> для фронтенда."""
        return {
            "id": self.id,
            "languages": [o.model_dump() for o in self.languages],
            "assets": self.assets.model_dump(),
        }