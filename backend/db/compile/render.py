"""Два рендерера IR в два диалекта MongoDB.

`render_match` — язык запросов ($match): решает, какие предложения вернутся.
`render_expr`  — язык выражений ($addFields): решает, какие токены подсветятся.

Оба принимают один и тот же список условий.
"""

from __future__ import annotations

from typing import Any

from backend.core.ir import AnyOf, Condition, Constraint, Scope

# Как адресуется поле в каждом из диалектов.
# В $match условия по токену живут внутри {tokens: {$elemMatch: {...}}},
# поэтому путь там относительный.
_MATCH_PREFIX = {
    Scope.SENTENCE: "",
    Scope.TOKEN: "",
    Scope.TAGSET: "tagsets.",
}

_EXPR_PREFIX = {
    Scope.TOKEN: "",
    Scope.TAGSET: "tagsets.",
}


def _match_leaf(c: Constraint) -> tuple[str, Any]:
    path = _MATCH_PREFIX[c.scope] + c.path

    if c.op == "exists":
        return path, {"$exists": True}
    if c.op == "regex":
        return path, {"$regex": c.values[0], "$options": "i"}
    return path, {"$in": list(c.values)}


def render_match(conditions: list[Condition]) -> dict:
    """IR -> тело $match для одного запроса пользователя."""
    top: dict[str, Any] = {}
    elem: dict[str, Any] = {}
    disjunctions: list[dict] = []

    for cond in conditions:
        if isinstance(cond, AnyOf):
            disjunctions.append(
                {"$or": [dict([_match_leaf(o)]) for o in cond.options]}
            )
            continue

        path, value = _match_leaf(cond)
        if cond.scope is Scope.SENTENCE:
            top[path] = value
        else:
            elem[path] = value

    if len(disjunctions) == 1:
        elem.update(disjunctions[0])
    elif disjunctions:
        elem["$and"] = disjunctions

    if elem:
        top["tokens"] = {"$elemMatch": elem}
    return top


def _expr_leaf(c: Constraint, var: str) -> dict:
    field = f"{var}.{_EXPR_PREFIX[c.scope]}{c.path}"

    if c.op == "exists":
        return {"$ne": [{"$ifNull": [field, None]}, None]}
    if c.op == "regex":
        return {"$regexMatch": {"input": field, "regex": c.values[0], "options": "i"}}
    # Тег может быть списком (Case=Obl + Case=Abl), а $in сравнивает его целиком:
    # для списка ищем пересечение со значениями, для скаляра — прежний $in.
    values = list(c.values)
    return {"$cond": [
        {"$isArray": field},
        {"$gt": [{"$size": {"$filter": {
            "input": field, "as": "v", "cond": {"$in": ["$$v", values]},
        }}}, 0]},
        {"$in": [field, values]},
    ]}


def render_expr(conditions: list[Condition], var: str = "$$x") -> list[dict]:
    """IR -> список условий для $filter по массиву токенов.

    Условия уровня предложения отбрасываются: у них нет токена, индекс
    которого можно было бы положить в final_indexes.
    """
    out: list[dict] = []

    for cond in conditions:
        if isinstance(cond, AnyOf):
            out.append({"$or": [_expr_leaf(o, var) for o in cond.options]})
            continue
        if cond.scope is Scope.SENTENCE:
            continue
        out.append(_expr_leaf(cond, var))

    return out
