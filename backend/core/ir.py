"""Промежуточное представление поискового запроса между пользовательской формы и компиляцией запроса к монге.
Два примитива: Constraint (одно ограничение) и AnyOf (ИЛИ между ними).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class Scope(str, Enum):
    """Уровень ограничения"""

    SENTENCE = "sentence"  # russian_text — поле предложения
    TOKEN = "token"        # tokens.lemma / .token / .translation
    TAGSET = "tagset"      # tokens.tagsets.*


OPERATION = Literal["in", "regex", "exists"]

@dataclass(frozen=True, slots=True)
class Constraint:
    """Одно ограничение на одно поле.

    op="in" -- ИЛИ между значениями
    op="regex" -- шаблон
    op="exists" -- булево значения, не принимает значений.
    """

    scope: Scope
    path: str
    op: OPERATION = "in"
    values: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.op == "exists" and self.values:
            raise ValueError(f"{self.path}: op='exists' не принимает значений")
        if self.op == "in" and not self.values:
            raise ValueError(f"{self.path}: op='in' требует хотя бы одно значение")
        if self.op == "regex" and len(self.values) != 1:
            raise ValueError(f"{self.path}: op='regex' требует ровно один шаблон")


@dataclass(frozen=True, slots=True)
class AnyOf:
    """ИЛИ между ограничениями на разные поля.

    Нужно там, где одна граммема может лежать в нескольких полях тегсета —
    например, лицо клитики в Person[clobj] или Person[clpos].
    """

    options: tuple[Constraint, ...]

    def __post_init__(self) -> None:
        if not self.options:
            raise ValueError("AnyOf не может быть пустым")


Condition = Constraint | AnyOf


def normalize(conditions: list[Condition]) -> list[Condition]:
    """Приводит набор условий к канонической форме.

    - AnyOf из одного варианта схлопывается в Constraint;
    - несколько op="in" на одно и то же поле объединяются по ИЛИ
    """

    merged: dict[tuple[Scope, str], list[str]] = {}
    order: list[tuple[Scope, str] | AnyOf | Constraint] = []

    for cond in conditions:
        if isinstance(cond, AnyOf):
            options = tuple(dict.fromkeys(cond.options))
            order.append(options[0] if len(options) == 1 else AnyOf(options))
            continue

        if cond.op != "in":
            if cond not in order:
                order.append(cond)
            continue

        key = (cond.scope, cond.path)
        if key not in merged:
            merged[key] = []
            order.append(key)
        for value in cond.values:
            if value not in merged[key]:
                merged[key].append(value)

    result: list[Condition] = []
    for item in order:
        if isinstance(item, tuple):
            scope, path = item
            result.append(Constraint(scope, path, "in", tuple(merged[item])))
        else:
            result.append(item)
    return result
