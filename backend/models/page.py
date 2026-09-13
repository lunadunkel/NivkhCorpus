# БАЗОВЫЕ UI-МОДЕЛИ
from pydantic import BaseModel, model_validator


class LanguageOption(BaseModel):
    """Опция <select> рядом со строкой поиска."""
    value: str
    label: str
    selected: bool = False

class Assets(BaseModel):
    """Корпусные css/js поверх общих."""
    styles: list[str] = []
    scripts: list[str] = []

class PageMeta(BaseModel):
    """Meta-информация страницы"""
    template: str
    title: str
    description: str = ""
    og_title: str | None = None
    og_description: str | None = None
    og_image_alt: str = ""
    og_type: str = "website"
    canonical: str = ""
    noindex: bool = False
    styles: list[str] = []

    @model_validator(mode="after")
    def _fill_og(self) -> "PageMeta":
        if self.og_title is None:
            self.og_title = self.title
        if self.og_description is None:
            self.og_description = self.description
        return self

class Vocabulary(BaseModel):
    letter: str
    example: str