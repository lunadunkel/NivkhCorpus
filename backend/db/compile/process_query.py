"""Разбор формы поиска в промежуточное представление."""

from dataclasses import dataclass, field

from backend.core.corpora import CorpusConfig
from backend.core.dictionaries import MISC, QUERY2DB
from backend.core.ir import OPERATION, AnyOf, Condition, Constraint, Scope, normalize

@dataclass
class OriginalQuery:
    """Один запрос пользователя, разобранный в набор условий."""
    conditions: list[Condition] = field(default_factory=list)
    language: str = ""
    search_type: str = ""


class QueryBuilder:
    def __init__(self, corpus: CorpusConfig, forms: list[dict]):
        self.corpus = corpus
        self.search = corpus.search
        # self.fields = corpus.search_fields()
        self.person_values = corpus.person_object_values()
        self.queries = self.process_queries(forms)

    def _word_field(self, language: str, search_type: str) -> tuple[Scope, str, OPERATION] | None:
        """Поле, по которому ищется введённое слово."""
        if language == self.search.meta_language:
            if search_type == "lemma":
                return Scope.TOKEN, self.search.translation_field, "in"
            if search_type == "token":
                return Scope.SENTENCE, self.search.sentence_text_field, "regex"
            return None

        if search_type == "lemma":
            return Scope.TOKEN, self.search.lemma_field, "in"
        if search_type == "token":
            return Scope.TOKEN, self.search.token_field, "in"
        return None

    def _word_conditions(self, language: str, search_type: str, word: str | None) -> list[Condition]:
        if not word:
            return []

        spec = self._word_field(language, search_type)
        if spec is None:
            return []

        scope, path, op = spec
        return [Constraint(scope, path, op, (word,))]


    def _grammar_conditions(self, form: dict) -> list[Condition]:
        conditions: list[Condition] = []

        # Идём по блокам конфига, а не по форме: имя инпута попадает в запрос как есть
        for mode, fields in self.corpus.search_groups():
            options: list[Constraint] = []

            for name, allowed in fields.items():
                raw = form.get(name)
                if not raw:
                    continue

                values = tuple(value
                    for value in (raw if isinstance(raw, list) else [raw])
                    if value in allowed
                )
                if values:
                    options.append(Constraint(Scope.TAGSET, name, "in", values))

            if not options:
                continue

            if mode == "any" and len(options) > 1:
                conditions.append(AnyOf(tuple(options)))
            else:
                conditions.extend(options)

        person_object = self._person_object(form)
        if person_object is not None:
            conditions.append(person_object)

        return conditions

    def _person_object(self, form: dict) -> Condition | None:
        """Граммема, живущая сразу в нескольких полях тегсета."""
        config = self.search.person_object
        if config is None:
            return None

        raw = form.get(config.field) or []
        person = tuple(
            v for v in (raw if isinstance(raw, list) else [raw])
            if v in self.person_values
        )
        selected = [path for name, path in config.paths.items() if form.get(name)]

        if not (person or selected):
            return None

        paths = selected or list(config.paths.values())

        if person:
            options = tuple(
                Constraint(Scope.TAGSET, path, "in", person) for path in paths
            )
        else:
            options = tuple(Constraint(Scope.TAGSET, path, "exists") for path in paths)

        return options[0] if len(options) == 1 else AnyOf(options)


    def process_queries(self, forms: list[dict]) -> list[OriginalQuery]:
        queries = []

        for form in forms:
            search_type = form.get("search-type")
            if search_type is None:
                raise ValueError("Не задан тип поиска")

            language = form.get("language-select")
            if language is None:
                raise ValueError("Не задан язык поиска")

            conditions = self._word_conditions(
                language, search_type, form.get("input_word") or None
            )
            conditions += self._grammar_conditions(form)

            queries.append(
                OriginalQuery(
                    conditions=normalize(conditions),
                    language=language,
                    search_type=search_type,
                )
            )

        return queries