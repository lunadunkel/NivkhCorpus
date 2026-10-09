"""Строка грамматических признаков <-> IR.

Нотация та же, что выдаёт `ir_text.format_grammar`:

    VerbForm=Conv & Person[word]=2
    (POS=(NOUN|VERB)|Classifier=Yes) & Case=(Dat|Loc)
    Person[clpos]                      -- поле есть, значение любое

`|` — ИЛИ, `&` — И. Скобки только группируют ИЛИ: `(A & B) | C` в IR
не выражается, поэтому это ошибка. Поля и значения проверяются по YAML:
имя поля уходит в запрос к монге, пропускать произвольное нельзя.
"""

import re
from collections import defaultdict

from backend.core.ir import AnyOf, Condition, Constraint, Scope
from backend.models.corpus import CorpusConfig
from backend.models.derived import person_object_values, search_fields

GRAMMAR_FIELD = "added-gram-features"

_TOKEN = re.compile(r"\s*(?:([()|&=])|([^\s()|&=]+))")


class GramQueryError(ValueError):
    def __init__(self, message: str, frame: int | None = None):
        super().__init__(message)
        self.message = message
        self.frame = frame


def allowed_fields(corpus: CorpusConfig) -> dict[str, set[str]]:
    """Поле тегсета -> допустимые значения, включая Person[clobj]/[clpos]."""
    fields = search_fields(corpus)
    person = corpus.search.person_object
    if person is not None:
        for path in person.paths.values():
            fields[path] = person_object_values(corpus)
    return fields


def _resolve(name: str, options, what: str) -> str:
    """Точное совпадение, иначе единственное без учёта регистра."""
    if name in options:
        return name
    found = [o for o in options if o.lower() == name.lower()]
    if len(found) == 1:
        return found[0]
    raise GramQueryError(f"неизвестное {what} «{name}»")


class _Parser:
    def __init__(self, text: str, fields: dict[str, set[str]]):
        self.fields = fields
        self.tokens = []
        pos = 0
        text = text.rstrip()
        while pos < len(text):
            m = _TOKEN.match(text, pos)
            self.tokens.append(m.group(1) or m.group(2))
            pos = m.end()
        self.i = 0

    def peek(self) -> str | None:
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def take(self, expected: str | None = None) -> str:
        tok = self.peek()
        if tok is None:
            raise GramQueryError("строка оборвалась" + (f", ожидалось «{expected}»" if expected else ""))
        if expected and tok != expected:
            raise GramQueryError(f"ожидалось «{expected}», а стоит «{tok}»")
        self.i += 1
        return tok

    def name(self) -> str:
        tok = self.take()
        if tok in "()|&=":
            raise GramQueryError(f"ожидался признак, а стоит «{tok}»")
        return tok

    def query(self) -> list[list[Constraint]]:
        groups = [self.group()]
        while self.peek() == "&":
            self.take()
            groups.append(self.group())
        if self.peek() is not None:
            raise GramQueryError(f"лишнее «{self.peek()}»")
        return groups

    def group(self) -> list[Constraint]:
        out = self.item()
        while self.peek() == "|":
            self.take()
            out += self.item()
        return out

    def item(self) -> list[Constraint]:
        if self.peek() == "(":
            self.take()
            out = self.group()
            if self.peek() == "&":
                raise GramQueryError("внутри скобок можно только |, а & ставится между ними")
            self.take(")")
            return out
        return [self.atom()]

    def atom(self) -> Constraint:
        path = _resolve(self.name(), self.fields, "поле")
        if self.peek() != "=":
            return Constraint(Scope.TAGSET, path, "exists")
        self.take()
        if self.peek() == "(":
            self.take()
            raw = [self.name()]
            while self.peek() == "|":
                self.take()
                raw.append(self.name())
            self.take(")")
        else:
            raw = [self.name()]
        values = tuple(dict.fromkeys(_resolve(v, self.fields[path], f"значение {path}") for v in raw))
        return Constraint(Scope.TAGSET, path, "in", values)


def _merge(options: list[Constraint]) -> Condition:
    """Одна группа ИЛИ -> Constraint или AnyOf; значения одного поля сливаются."""
    merged: dict[str, list[str]] = {}
    order: list[str | Constraint] = []
    for c in options:
        if c.op != "in":
            if c not in order:
                order.append(c)
            continue
        if c.path not in merged:
            merged[c.path] = []
            order.append(c.path)
        merged[c.path] += [v for v in c.values if v not in merged[c.path]]

    out = [Constraint(Scope.TAGSET, o, "in", tuple(merged[o])) if isinstance(o, str) else o for o in order]
    return out[0] if len(out) == 1 else AnyOf(tuple(out))


def parse_grammar(text: str, corpus: CorpusConfig) -> list[Condition]:
    if not text or not text.strip():
        return []
    conditions = [_merge(group) for group in _Parser(text, allowed_fields(corpus)).query()]

    # render_match кладёт поле в словарь: два И на одно поле затрут друг друга
    seen = set()
    for c in conditions:
        if isinstance(c, Constraint):
            if c.path in seen:
                raise GramQueryError(f"{c.path} указано дважды; варианты пишутся через |")
            seen.add(c.path)
    return conditions


def to_checkboxes(conditions: list[Condition], corpus: CorpusConfig) -> dict[str, list[str]]:
    """IR -> какие галочки отметить в модале (name -> значения)."""
    person = corpus.search.person_object
    toggle_by_path = {path: name for name, path in person.paths.items()} if person else {}
    toggle_value = {
        value.name(block.id): value.value
        for block in corpus.grammar for value in block.values
        if value.name(block.id) in toggle_by_path.values()
    }

    out: dict[str, list[str]] = defaultdict(list)
    for cond in conditions:
        for c in cond.options if isinstance(cond, AnyOf) else (cond,):
            if c.path in toggle_by_path:
                toggle = toggle_by_path[c.path]
                out[toggle] = [toggle_value.get(toggle, "yes")]
                out[person.field] += [v for v in c.values if v not in out[person.field]]
            elif c.op == "in":
                out[c.path] += [v for v in c.values if v not in out[c.path]]
    return dict(out)


def _canon(cond: Condition):
    if isinstance(cond, AnyOf):
        return frozenset(_canon(o) for o in cond.options)
    return (cond.path, cond.op, frozenset(cond.values))


def same_conditions(a: list[Condition], b: list[Condition]) -> bool:
    """Равенство без учёта порядка: строку человек мог написать в любом."""
    return {_canon(c) for c in a} == {_canon(c) for c in b} and len(a) == len(b)
