"""Индексы базы данных; вызывается на старте для каждого корпуса."""

from backend.core.config import COLLECTION_JOB, COLLECTION_RESULTS, COLLECTION_SENT
from backend.core.deps import get_corpus
from backend.db.database import get_collection

JOB_TTL_SECONDS = 3600

def get_indexed_fields(lang: str) -> list[str]:
    cfg = get_corpus(lang)
    fields = cfg.indexes

    if not isinstance(fields, list) or not all(isinstance(f, str) and f.strip() for f in fields):
        raise ValueError(
            f"[{lang}] indexes must be a list of non-empty strings"
        )
    return list(dict.fromkeys(f.strip() for f in fields))

async def ensure_indexes(lang: str) -> None:
    jobs = get_collection(lang, COLLECTION_JOB)
    results = get_collection(lang, COLLECTION_RESULTS)
    sentences = get_collection(lang, COLLECTION_SENT)

    await jobs.create_index("query_hash", unique=True)
    await jobs.create_index("created_at", expireAfterSeconds=JOB_TTL_SECONDS)

    await results.create_index("job_id")
    await results.create_index("created_at", expireAfterSeconds=JOB_TTL_SECONDS)
    indexes = get_indexed_fields(lang)

    for field in indexes:
        await sentences.create_index(field)
