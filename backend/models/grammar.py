# Грамматический модал

from typing import Literal
from pydantic import BaseModel


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
    show: bool = True
    values: list[GrammarValue]

    @property
    def visible_values(self) -> list[GrammarValue]:
        return [v for v in self.values if v.show]

class Layout(BaseModel):
    """Расположение блоков в грамматическом модале"""
    columns: list[list[str]] = []