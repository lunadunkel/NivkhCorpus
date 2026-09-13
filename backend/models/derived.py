"""Что выводится из корпусного конфига.
 
Схема поиска для QueryBuilder и раскладка модала для шаблонов. Всё это
считается из CorpusConfig и ничего в нём не меняет, поэтому живёт
отдельно от модели: сам конфиг описывает форму YAML, а не то, как ей
пользуются.
 
Каждая функция считает результат заново. Конфиг маленький (у нивхского
14 блоков и 79 значений), полный пересчёт — около 50 мкс, то есть доли
процента от запроса к монге.
"""
 
from dataclasses import dataclass
from typing import Literal

from backend.models.corpus import CorpusConfig
from backend.models.grammar import AllowedValues, GrammarBlock

 
 
@dataclass(frozen=True)
class SearchGroup:
    """Один блок грамматики, готовый к сборке в запрос.
 
    `match` - тип объединение блока:
    - all = конъюнкция
    - any = дизъюнкция
    """

    id: str
    match: Literal["all", "any"]
    fields: AllowedValues
 
 
def reserved_fields(corpus: CorpusConfig) -> set[str]:
    """Имена, которые разбирает не общий путь, а person_object."""
    person_object = corpus.search.person_object
    if person_object is None:
        return set()
    return {person_object.field, *person_object.paths}
 
 
def search_groups(corpus: CorpusConfig) -> list[SearchGroup]:
    """Грамматические блоки в виде, пригодном для сборки запроса.
 
    Разбивка по блокам нужна из-за match: объединять галочки по ИЛИ или
    по И — свойство блока, а не корпуса."""
    reserved = reserved_fields(corpus)
    groups = []
 
    for block in corpus.grammar:
        fields: AllowedValues = {}
        for name, values in block.fields().items():
            if name not in reserved:
                fields[name] = values
        if fields:
            groups.append(SearchGroup(id=block.id, match=block.match, fields=fields))
 
    return groups

def person_object_block(corpus: CorpusConfig) -> str | None:
    """id блока, в котором нарисованы переключатели person_object."""
    config = corpus.search.person_object
    if config is None:
        return None
 
    for block in corpus.grammar:
        for value in block.values:
            if value.name(block.id) in config.paths:
                return block.id
    return None
 
def search_fields(corpus: CorpusConfig) -> AllowedValues:
    """То же, что search_groups, но без разбивки на блоки."""
    out: AllowedValues = {}
    for group in search_groups(corpus):
        for name, values in group.fields.items():
            if name not in out:
                out[name] = set()
            out[name].update(values)
    return out
 
 
def person_object_values(corpus: CorpusConfig) -> set[str]:
    """Значения, которые вправе прийти в поле person_object."""
    person_object = corpus.search.person_object
    if person_object is None:
        return set()
 
    values: set[str] = set()
    for block in corpus.grammar:
        values.update(block.fields().get(person_object.field, set()))
    return values
 
 
def blocks_by_id(corpus: CorpusConfig) -> dict[str, GrammarBlock]:
    """Блоки грамматики по их id."""
    out = {}
    for block in corpus.grammar:
        out[block.id] = block
    return out
 
 
def columns(corpus: CorpusConfig) -> list[list[GrammarBlock]]:
    """Блоки, разложенные по колонкам модала."""
    by_id = blocks_by_id(corpus)
    out = []
 
    for column in corpus.layout.columns:
        visible = []
        for block_id in column:
            block = by_id[block_id]
            visible.append(block)
        out.append(visible)
 
    return out
 
 
def public_dict(corpus: CorpusConfig) -> dict:
    """То, что уезжает в <script id="corpus-config"> для фронтенда."""
    return {
        "id": corpus.id,
        "languages": [option.model_dump() for option in corpus.languages],
        "assets": corpus.assets.model_dump(),
    }

 