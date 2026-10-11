import asyncio
from datetime import datetime
from collections import OrderedDict
from typing import Any, Union
from bson import ObjectId
from backend.core.config import CORPORA
from backend.db.database import get_collection

async def fetch_corpus_stats(corpus_id: str) -> dict[str, Any]:
    """Тексты, предложения и токены одного корпуса из коллекции statistics.

    Пока данные не импортированы, возвращает нули.
    """
    collection = get_collection(corpus_id, "statistics")
    result: dict[Any, Any] | None = await collection.find_one({}, {"_id": 0})
    if result is None:
        result = {'total_texts': 0, 'total_sentences': 0, 'total_tokens': 0}
    return result


async def fetch_texts(corpus_id: str) -> list[dict[str, Any]]:
    """Все документы коллекции texts: по одному на текст корпуса."""
    collection = get_collection(corpus_id, "texts")
    return await collection.find({}, {"_id": 0}).to_list(length=None)


async def fetch_per_corpus():
    data = {}
    for corpus, items in CORPORA.items():
        lang_family = items.language_family
        collection = get_collection(corpus, "statistics")
        result: dict[Any, Any] | None = await collection.find_one({}, {"_id": 0})
        if result is None:
            result = {'total_texts': 0, 'total_sentences': 0, 'total_tokens': 0}
        result['lang_family'] = lang_family
        result['lang_label'] = items.name['ru']
        result['enabled'] = items.enabled
        data[corpus] = result
    result = OrderedDict(sorted(data.items(), key=lambda x: x[1]['total_texts'], reverse=True))
    return result

if __name__ == "__main__":
    asyncio.run(fetch_per_corpus())