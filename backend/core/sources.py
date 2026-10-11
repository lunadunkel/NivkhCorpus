"""Источники текстов корпуса: группировка коллекции texts по полю source."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SourceText:
    """Один текст внутри источника."""
    file: str
    title_n: str
    title_r: str
    genre: str
    dialect: str
    year: int | None
    num_sentences: int
    num_tokens: int


@dataclass(frozen=True)
class SourceGroup:
    """Один источник и все тексты корпуса, взятые из него."""
    source: str
    url: str
    texts: list[SourceText]

    @property
    def num_tokens(self) -> int:
        return sum(text.num_tokens for text in self.texts)


def _clean_source(raw: str | None) -> str:
    """Схлопывает пробелы и убирает хвостовые запятые и точки с запятой,
    которые остаются после того, как из строки вынули ссылку."""
    return " ".join((raw or "").split()).rstrip(" ,;")


def group_sources(docs: list[dict[str, Any]]) -> list[SourceGroup]:
    """Документы texts -> источники.

    Источник определяется парой (source, source_url). Первыми идут источники
    с наибольшим числом текстов, затем по алфавиту. Тексты без источника
    собираются в одну группу с пустым source и стоят в конце. Внутри
    источника тексты идут по году, затем по названию.
    """
    grouped: dict[tuple[str, str], list[SourceText]] = {}
    for doc in docs:
        key = (_clean_source(doc.get("source")), (doc.get("source_url") or "").strip())
        grouped.setdefault(key, []).append(SourceText(
            file=doc.get("file", ""),
            title_n=(doc.get("title_n") or "").strip(),
            title_r=(doc.get("title_r") or "").strip(),
            genre=doc.get("genre") or "",
            dialect=doc.get("dialect") or "",
            year=doc.get("year") or None,
            num_sentences=doc.get("num_sentences") or 0,
            num_tokens=doc.get("num_tokens") or 0,
        ))

    groups = []
    for (source, url), texts in grouped.items():
        texts.sort(key=lambda t: (t.year or 0, (t.title_r or t.title_n or t.file).casefold()))
        groups.append(SourceGroup(source=source, url=url, texts=texts))

    groups.sort(key=lambda g: (not g.source and not g.url, -len(g.texts), g.source.casefold()))
    return groups
