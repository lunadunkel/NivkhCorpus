"""Индексы базы данных; вызывается на старте для каждого корпуса."""

from backend.core.config import COLLECTION_JOB, COLLECTION_RESULTS, COLLECTION_SENT
from backend.db.database import get_collection

JOB_TTL_SECONDS = 3600

# Поля тегсета, по которым чаще всего фильтруют. Список корпусный —
# после переезда маппинга в YAML берётся из CorpusConfig.
SENTENCE_INDEXED_FIELDS = [
    "tokens.token",
    "tokens.lemma",
    "tokens.tagsets.POS",
    "tokens.tagsets.Case",
    "tokens.tagsets.Tense",
    "tokens.tagsets.Person[word]",
    "tokens.tagsets.Number[word]",
]

async def ensure_indexes(lang: str) -> None:
    jobs = get_collection(lang, COLLECTION_JOB)
    results = get_collection(lang, COLLECTION_RESULTS)
    sentences = get_collection(lang, COLLECTION_SENT)

    await jobs.create_index("query_hash", unique=True)
    await jobs.create_index("created_at", expireAfterSeconds=JOB_TTL_SECONDS)

    await results.create_index("job_id")
    await results.create_index("created_at", expireAfterSeconds=JOB_TTL_SECONDS)

    for field in SENTENCE_INDEXED_FIELDS:
        await sentences.create_index(field)
