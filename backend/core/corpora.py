"""Модели pydantic с настройками корпусов"""

from pydantic import BaseModel, Field, PrivateAttr, model_validator


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
    field: str | None = None
    show: bool = True

    def name(self, block_id: str) -> str:
        return self.field or block_id

class GrammarBlock(BaseModel):
    id: str
    group: bool = False
    label: str
    tooltip: str = ""
    html_id: str | None = None
    select_all: bool = True
    show: bool = True
    values: list[GrammarValue]

    @property
    def visible_values(self) -> list[GrammarValue]:
        return [v for v in self.values if v.show]

class PersonObject(BaseModel):
    """Граммема, которая может лежать в нескольких полях тегсета сразу.

    `paths` — имя чекбокса-переключателя -> поле тегсета. Если ни один
    переключатель не отмечен, ищем во всех полях (ИЛИ).
    """
    field: str
    paths: dict[str, str]

class SearchConfig(BaseModel):
    """Как поля формы переводятся в схему БД."""
    meta_language: str = "russian"
    sentence_text_field: str = "russian_text"
    translation_field: str = "translation"
    lemma_field: str = "lemma"
    token_field: str = "token"
    person_object: PersonObject | None = None

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
    search: SearchConfig = Field(default_factory=SearchConfig)
    keyboard: list[list[str]] = []
    assets: Assets = Field(default_factory=Assets)
    pages: dict[str, PageMeta] = {}
    layout: Layout = Field(default_factory=Layout)
    grammar: list[GrammarBlock] = []
    dictionary: list[Vocabulary] = []
    alphabet_order: list[str] = []

    _fields: dict[str, set[str]] | None = PrivateAttr(default=None)

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
    
    @model_validator(mode="after")
    def _check_fields(self) -> "CorpusConfig":
        po = self.search.person_object
        reserved = {po.field, *po.paths} if po else set()

        for block in self.grammar:
            if not block.group:
                continue
            for value in block.values:
                if value.field is None:
                    raise ValueError(
                        f"{self.id}: {block.id}/{value.label} — блок только "
                        f"группирует, у значения должно быть своё field"
                    )

        for name in self.search_fields():
            if name in reserved:
                continue
            if name.startswith("$") or "." in name:
                raise ValueError(f"{self.id}: недопустимое поле тегсета {name!r}")

        return self
    
    def person_object_values(self) -> set[str]:
        """Значения, которые вправе прийти в поле person_object."""
        po = self.search.person_object
        if po is None:
            return set()
        return {
            v.value
            for b in self.grammar
            for v in b.values
            if v.name(b.id) == po.field
        }

    def search_fields(self) -> dict[str, set[str]]:
        """Поле тегсета -> допустимые значения.

        список разрешённого: имена инпутов приходят от клиента и 
        попадают в запрос как есть, поэтому их надо сверять
        с конфигом. Переключатели person_object сюда не входят — у них своя
        логика в QueryBuilder.
        """
        if self._fields is not None:
            return self._fields

        po = self.search.person_object
        reserved = {po.field, *po.paths} if po else set()

        out: dict[str, set[str]] = {}
        for block in self.grammar:
            for value in block.values:
                name = value.name(block.id)
                if name in reserved:
                    continue
                out.setdefault(name, set()).add(value.value)

        self._fields = out
        return out

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