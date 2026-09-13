"""Разбор формы поиска в промежуточное представление."""

from dataclasses import dataclass, field

from backend.models.corpus import CorpusConfig
from backend.core.ir import OPERATION, AnyOf, Condition, Constraint, Scope, normalize
from backend.models.derived import SearchGroup, person_object_values, search_groups, person_object_block

@dataclass
class OriginalQuery:
    """Один запрос пользователя, разобранный в набор условий."""
    conditions: list[Condition] = field(default_factory=list)
    language: str = ""
    search_type: str = ""


def selected(form: dict, name: str) -> list[str]:
    """Что отмечено в поле формы в унифицированном виде"""
    raw = form.get(name)
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    return [raw]


class QueryBuilder:
    def __init__(self, corpus: CorpusConfig, forms: list[dict]):
        self.corpus = corpus
        self.search = corpus.search
        self.person_values = person_object_values(corpus)
        self.person_block = person_object_block(corpus)
        self.queries = self.process_queries(forms)

    def process_queries(self, forms: list[dict]) -> list[OriginalQuery]:
        """Разбор всех форм"""
        return [self._process_form(form) for form in forms]

    def _process_form(self, form: dict) -> OriginalQuery:
        """Разбор каждой формы по отдельности"""
        search_type = form.get("search-type")
        if search_type is None:
            raise ValueError("Не задан тип поиска")

        language = form.get("language-select")
        if language is None:
            raise ValueError("Не задан язык поиска")

        conditions: list[Condition] = []

        word = self._word_condition(language, search_type, form.get("input_word"))
        if word is not None:
            conditions.append(word)

        conditions += self._grammar_conditions(form)

        return OriginalQuery(
            conditions=normalize(conditions),
            language=language,
            search_type=search_type,
        )
    def _word_condition(self, language: str, search_type: str, word: str | None) -> Constraint | None:
        """Условие на слово из строки поиска по типу поиска и языку поиска"""
        if not word:
            return None

        if language == self.search.meta_language:
            if search_type == "lemma":
                return Constraint(Scope.TOKEN, self.search.translation_field, "in", (word,))
            if search_type == "token":
                return Constraint(Scope.SENTENCE, self.search.sentence_text_field, "regex", (word,))
            return None

        if search_type == "lemma":
            return Constraint(Scope.TOKEN, self.search.lemma_field, "in", (word,))
        if search_type == "token":
            return Constraint(Scope.TOKEN, self.search.token_field, "in", (word,))
        return None

    def _grammar_conditions(self, form: dict) -> list[Condition]:
        """идёт по блокам грамматики из конфига. Для каждого блока зовёт _block_options, потом решает, как склеить полученные ограничения"""
        conditions: list[Condition] = []
        person_object = self._person_object_constraints(form)

        for group in search_groups(self.corpus):
            options = self._block_options(form, group)

            if group.id == self.person_block:
                options += person_object

            if not options:
                continue

            if group.match == "any" and len(options) > 1:
                conditions.append(AnyOf(tuple(options)))
            else:
                conditions.extend(options)

        return conditions

    def _block_options(self, form: dict, group: SearchGroup) -> list[Constraint]:
        options: list[Constraint] = []

        for name, allowed in group.fields.items():
            values = tuple(value for value in selected(form, name) if value in allowed)
            if values:
                options.append(Constraint(Scope.TAGSET, name, "in", values))

        return options
    
    def _person_object_constraints(self, form: dict) -> list[Constraint]:
        """Граммема, живущая сразу в нескольких полях тегсета.

        Переключатели (у нивхского clobj и clpos) выбирают поля, в которых
        искать; если не отмечен ни один — ищем во всех. Отмеченное лицо
        задаёт значение, без него достаточно наличия поля.
        """
        config = self.search.person_object
        if config is None:
            return []

        person = tuple(
            value for value in selected(form, config.field)
            if value in self.person_values
        )
        chosen = [path for name, path in config.paths.items() if form.get(name)]

        if not person and not chosen:
            return []

        paths = chosen or list(config.paths.values())

        if person:
            return [Constraint(Scope.TAGSET, path, "in", person) for path in paths]
        return [Constraint(Scope.TAGSET, path, "exists") for path in paths]
       
