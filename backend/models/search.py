from pydantic import BaseModel


class PersonObject(BaseModel):
    """Граммема PO -- в нескольких полях тегсета сразу.

    `paths` — отмеченный чекбокс
    """
    field: str
    paths: dict[str, str]

class SearchConfig(BaseModel):
    """Как поля формы переводятся в схему БД."""
    meta_language: str = "russian"
    sentence_text_field: str = "russian_text"
    translation_field: str = "translation"
    lemma_field: str = "lemma"
    token_field: str = "token"
    person_object: PersonObject | None = None