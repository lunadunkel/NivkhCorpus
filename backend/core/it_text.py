"""IR -> строка грамматических признаков для показа пользователю.
"""

from backend.core.ir import AnyOf, Condition, Constraint, Scope


def _group(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"({'|'.join(items)})"


def _constraint(c: Constraint) -> str:
    if c.op == "exists":
        return c.path
    return f"{c.path}={_group(list(c.values))}"


def format_grammar(conditions: list[Condition]) -> str:
    """Грамматическая часть одного запроса. Условия на слово пропускаются."""
    parts = []
    for cond in conditions:
        if isinstance(cond, AnyOf):
            parts.append(_group([_constraint(o) for o in cond.options]))
        elif cond.scope is Scope.TAGSET:
            parts.append(_constraint(cond))
        elif cond.scope is Scope.TOKEN:
            parts.append(f"{_group(list(cond.values))}")
    return " & ".join(parts)