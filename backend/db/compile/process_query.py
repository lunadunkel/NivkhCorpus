"""Разбор формы поиска в промежуточное представление."""

from dataclasses import dataclass, field

from backend.core.dictionaries import MISC, QUERY2DB
from backend.core.ir import OPERATION, AnyOf, Condition, Constraint, Scope, normalize

# Поле токена, по которому ищется введённое слово.
_WORD_FIELD: dict[
    tuple[str, str],
    tuple[Scope, str, OPERATION]
] =  {
    ("russian", "lemma"): (Scope.TOKEN, "translation", "in"),
    ("russian", "token"): (Scope.SENTENCE, "russian_text", "regex"),
}
_DEFAULT_WORD_FIELD: dict[
    str,
    tuple[Scope, str, OPERATION]
] = {
    "lemma": (Scope.TOKEN, "lemma", "in"),
    "token": (Scope.TOKEN, "token", "in"),
}

_PERSON_OBJECT_PATHS = ("Person[clobj]", "Person[clpos]")


@dataclass
class OriginalQuery:
    """Один запрос пользователя, разобранный в набор условий."""

    conditions: list[Condition] = field(default_factory=list)
    language: str = "niv"
    search_type: str = "lemma"


class QueryBuilder:
    def __init__(self, query: list[dict]):
        self.language = query[0]["language-select"]
        self.queries = self.process_queries(query)

    def _word_conditions(self, search_type: str, word: str | None) -> list[Condition]:
        if not word:
            return []

        spec = _WORD_FIELD.get((self.language, search_type))
        if spec is None:
            spec = _DEFAULT_WORD_FIELD.get(search_type)
        if spec is None:
            return []

        scope, path, op = spec
        return list([Constraint(scope, path, op, (word,))])

    def _grammar_conditions(self, query: dict) -> list[Condition]:
        conditions: list[Condition] = []

        for ui_key, db_key in QUERY2DB.items():

            value = query.get(ui_key)
            if not value:
                continue

            if not isinstance(value, list):
                value = [value]

            feature = MISC.get(ui_key)
            if feature is None:
                conditions.append(Constraint(Scope.TAGSET, db_key, "in", tuple(value)))
                continue

            for val in value:
                path, db_value = feature[val].split("=")
                conditions.append(Constraint(Scope.TAGSET, path, "in", (db_value,)))

        person_object = self._person_object(query)
        if person_object is not None:
            conditions.append(person_object)

        return conditions

    def _person_object(self, query: dict) -> Condition | None:
        """Лицо объекта или посессора: одна граммема в двух полях тегсета."""
        person = query.get("person_obj[]")
        clobj = bool(query.get("clobj"))
        clpos = bool(query.get("clpos"))

        if not (person or clobj or clpos):
            return None

        selected = [
            path for path, on in zip(_PERSON_OBJECT_PATHS, (clobj, clpos)) if on
        ]
        paths = selected or list(_PERSON_OBJECT_PATHS)
        # paths = selected

        if person:
            if not isinstance(person, list):
                person = [person]
            options = tuple(
                Constraint(Scope.TAGSET, path, "in", tuple(person)) for path in paths
            )
        else:
            options = tuple(Constraint(Scope.TAGSET, path, "exists") for path in paths)

        return options[0] if len(options) == 1 else AnyOf(options)

    def process_queries(self, query: list[dict]) -> list[OriginalQuery]:
        queries = []

        for q in query:
            search_type = q.get("search-type")
            if search_type is None:
                raise ValueError("Не задан тип поиска")
            conditions = self._word_conditions(search_type, q.get("input_word") or None)
            conditions += self._grammar_conditions(q)

            queries.append(
                OriginalQuery(
                    conditions=normalize(conditions),
                    language=self.language,
                    search_type=search_type,
                )
            )

        return queries
