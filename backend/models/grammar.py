from typing import Literal

from pydantic import BaseModel, model_validator


type AllowedValues = dict[str, set[str]]
"""Поле тегсета -> значения, которые по нему разрешено искать.

Например: {"POS": {"NOUN", "VERB"}, "Polarity": {"Neg"}}.
"""

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
    """Блок чекбоксов в модале.

    `match` - тип объединение блока:
    - all = конъюнкция
    - any = дизъюнкция
    """
    id: str
    group: bool = False
    match: Literal["all", "any"] = "any"
    label: str
    tooltip: str = ""
    html_id: str | None = None
    select_all: bool = True
    values: list[GrammarValue]

    @model_validator(mode="after")
    def _values_have_a_field(self) -> "GrammarBlock":
        if not self.group:
            return self
        for value in self.values:
            if value.field is None:
                raise ValueError(
                    f"{self.id}/{value.label} — блок только группирует, "
                    f"у значения должно быть своё field"
                )
        return self

    @model_validator(mode="after")
    def _checkboxes_are_unique(self) -> "GrammarBlock":
        """Внутри блока нет двух чекбоксов с одинаковой парой имя=значение."""
        seen = set()
        duplicates = set()
        for value in self.values:
            checkbox = f"{value.name(self.id)}={value.value}"
            if checkbox in seen:
                duplicates.add(checkbox)
            seen.add(checkbox)

        if duplicates:
            raise ValueError(
                f"{self.id}: повторяющиеся чекбоксы {sorted(duplicates)}"
            )
        return self

    def fields(self) -> dict[str, set[str]]:
        """Поле тегсета -> допустимые в этом блоке значения."""
        out: dict[str, set[str]] = {}
        for value in self.values:
            name = value.name(self.id)
            if name not in out:
                out[name] = set()
            out[name].add(value.value)
        return out


class Layout(BaseModel):
    columns: list[list[str]] = []
