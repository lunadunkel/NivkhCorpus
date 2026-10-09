"""Предобработка json перед загрузкой в MongoDB.

    processing = Json2MongoProcessing(Path("data/karaim"), config["ingest"], "karaim")
    docs = processing.process_json("Solovej.json")
"""

from datetime import datetime
import json
import re
import unicodedata as ud
from pathlib import Path
from typing import Any, cast

# Строки, которыми в исходных данных обозначено «значения нет».
PLACEHOLDERS = {"None", "-", "", "Webpage unspecified"}

# Поля на языке оригинала и поля на языке описания: графика у них разная.
LANG_FIELDS = {"token", "lemma", "segmentation", "text", "segmented_text"}
BASE_META_FIELDS = {"gloss", "glossed_text"}

# Кириллические буквы и неотличимые от них латинские.
HOMOGLYPHS = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i", "ј": "j",
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O",
    "Р": "P", "С": "C", "Т": "T", "У": "Y", "Х": "X",
}
CYR_FROM_LAT = {lat: cyr for cyr, lat in HOMOGLYPHS.items()}
DATE_FORMAT = "%d.%m.%Y"

def is_cyrillic(char: str) -> bool:
    return "CYRILLIC" in ud.name(char, "")


def is_latin(char: str) -> bool:
    return "LATIN" in ud.name(char, "")


def fix_mixed_word(match: "re.Match[str]") -> str:
    """Латинские буквы в кириллическом слове: "Kитай" -> "Китай".

    Только для полей на языке описания. Там латиница законна сама по себе
    (глоссы PRS, 3.SG), поэтому слово правится, лишь если в нём смешаны обе
    графики.
    """
    word = match.group(0)
    if any(is_cyrillic(c) for c in word) and any(is_latin(c) for c in word):
        return "".join(CYR_FROM_LAT.get(c, c) for c in word)
    return word


class Json2MongoProcessing:
    def __init__(self, path: Path, config: dict[str, Any], corpus: str, meta_fields):
        """Args:
            path: папка с json-файлами корпуса
            config: секция `ingest:` из конфига корпуса
            corpus: id корпуса, попадёт в документы
            meta_fields: поля на языке перевода из секции `search:`"""
        self.path = path
        self.corpus = corpus
        self.meta_fields = BASE_META_FIELDS | set(meta_fields)
        self.latin = config["script"] == "latin"
        self.rename: dict[str, str] = config.get("rename", {})
        self.drop_fields: set[str] = set(config.get("drop_fields", []))
        self.strip_fields: set[str] = set(config.get("strip_punct", []))
        self.strip_chars: str = config.get("strip_chars", "")
        self.spelling: dict[str, str] = config.get("spelling", {})

    def process_json(self, filename: str) -> list[dict[str, Any]]:
        """Прочитать файл и вернуть документы, готовые к вставке в Mongo."""
        with open(self.path / filename, encoding="utf8") as file:
            loaded: Any = json.load(file)
        if not isinstance(loaded, list):
            raise TypeError(f"{filename}: ожидался список предложений")
        file_data = cast(list[dict[str, Any]], loaded)

        text_id = Path(filename).stem
        return [self.sentence(sent, text_id) for sent in file_data]

    def sentence(self, sent: dict[str, Any], text_id: str) -> dict[str, Any]:
        doc: dict[str, Any] = {
            "_id": f"{self.corpus}:{text_id}:{sent['id']}",
            "corpus": self.corpus,
            "text_id": text_id,
        }
        for key, value in sent.items():
            if key == "tokens" or key in self.drop_fields:
                continue
            if key == "metadata" and isinstance(value, dict):
                value = self.metadata(value)
            if isinstance(value, str):
                value = self.clean(value, key)
                if value in PLACEHOLDERS:
                    continue
            doc[key] = value

        doc["tokens"] = [self.token(tok, pos) for pos, tok in enumerate(sent["tokens"])]
        doc["length"] = len(doc["tokens"])
        return doc

    def metadata(self, meta: dict[str, Any]) -> dict[str, Any]:
        """Привести metadata к виду для Mongo: date из строки в datetime."""
        new_meta = dict(meta)
        raw = new_meta.pop("date", None)
        if isinstance(raw, str):
            raw = ud.normalize("NFC", raw).strip()
            if raw not in PLACEHOLDERS:
                try:
                    new_meta["date"] = datetime.strptime(raw, DATE_FORMAT)
                except ValueError:
                    raise ValueError(
                        f"metadata.date: ожидался формат ДД.ММ.ГГГГ, получено {raw!r}"
                    ) from None
        elif raw is not None:
            new_meta["date"] = raw   # уже не строка, не трогаем
        return new_meta

    def token(self, tok: dict[str, Any], pos: int) -> dict[str, Any]:
        new_tok: dict[str, Any] = {"idx": pos, "itoken": int(tok["itoken"])}
        for key, value in tok.items():
            if key in ("idx", "itoken", "tagsets") or key in self.drop_fields:
                continue
            if isinstance(value, str):
                value = self.clean(value, key)
                if value in PLACEHOLDERS:
                    continue
            new_tok[key] = value

        new_tok["tagsets"] = self.tagset(tok["tagsets"], tok["token"])
        return new_tok

    def clean(self, value: str, field: str) -> str:
        """Привести строку в порядок: графика, юникод, лишняя пунктуация."""
        value = ud.normalize("NFC", value).strip()
        if value in PLACEHOLDERS:
            return value
        if field in LANG_FIELDS:
            # поле целиком на языке оригинала, чужая графика тут вся лишняя
            table = HOMOGLYPHS if self.latin else CYR_FROM_LAT
            value = "".join(table.get(char, char) for char in value)
            for old, new in self.spelling.items():
                value = value.replace(old, new)
        elif field in self.meta_fields:
            value = re.sub(r"\w+", fix_mixed_word, value)
        if field in self.strip_fields and self.strip_chars:
            value = value.strip(self.strip_chars)
        return value

    def tagset(self, tagsets: list[list[str]], token: str) -> dict[str, Any]:
        """Список тегов в словарь: ["VERB", "Tense=Past"] -> {"POS": ..., "Tense": ...}."""
        if len(tagsets) != 1:
            raise ValueError(f"у токена {token!r} наборов тегов не один: {tagsets}")

        new_tagset: dict[str, Any] = {}
        for idx, tag in enumerate(tagsets[0]):
            if "=" in tag:
                key, value = tag.split("=", 1)
            elif idx == 0:
                key, value = "POS", tag   # часть речи идёт первой и без ключа
            else:
                raise ValueError(f"у токена {token!r} тег без ключа: {tag}")

            key = self.rename.get(key, key)
            if value in PLACEHOLDERS:
                continue

            old = new_tagset.get(key)
            if old is None:
                new_tagset[key] = value
            elif value in (old if isinstance(old, list) else [old]):
                continue   # Reflex=Yes дважды -> просто Yes
            elif isinstance(old, list):
                new_tagset[key] = [*old, value]   # третья морфема подряд
            else:
                new_tagset[key] = [old, value]    # Case=Obl + Case=Abl
        return new_tagset


if __name__ == "__main__":
    import sys

    import yaml

    with open(sys.argv[1], encoding="utf8") as config_file:
        config = yaml.safe_load(config_file)
    source = Path(sys.argv[2])
    search = config["search"]
    meta = {search["translation_field"], search["sentence_text_field"]}
    processing = Json2MongoProcessing(source.parent, config["ingest"], config["id"], meta)
    docs = processing.process_json(source.name)
    print(json.dumps(docs[:1], ensure_ascii=False, indent=2, default=str))
    print(f"{source.name}: {len(docs)} предложений, "
          f"{sum(len(d['tokens']) for d in docs)} токенов")
