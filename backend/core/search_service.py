import uuid
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError

from backend.core.config import COLLECTION_DICT, COLLECTION_JOB, COLLECTION_RESULTS, COLLECTION_SENT
from backend.models.corpus import CorpusConfig
from backend.db.compile.aggregation_compile import AggregatePipeline
from backend.db.compile.process_query import QueryBuilder
from backend.db.database import get_collection
from backend.db.repositories.jobs_repo import search_jobs
from backend.db.repositories.utils import clean, make_hash


def _to_object_id(doc_id: str) -> ObjectId | None:
    try:
        return ObjectId(doc_id)
    except (InvalidId, TypeError):
        return None


async def run_search_db(corpus: CorpusConfig, collection: AsyncIOMotorCollection, query: list[dict]):
    qb = QueryBuilder(corpus, forms=query)
    aggregation = AggregatePipeline(qb.queries).aggregate()
    cursor = collection.aggregate(aggregation)
    return await cursor.to_list(length=None)


async def search(corpus: CorpusConfig, query):
    lang = corpus.id
    jobs_collection = get_collection(lang, COLLECTION_JOB)
    sent_collection = get_collection(lang, COLLECTION_SENT)
    
    query_hash = make_hash(query)

    
    existing = await search_jobs.find_by_hash(jobs_collection, query_hash)
    if existing:
        return {"status": "ok", "job_id": existing["_id"]}

    result = await run_search_db(corpus, sent_collection, query)
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    try:
        await search_jobs.save(jobs_collection, {
                "_id": job_id,
                "query_hash": query_hash,
                "status": "done" if result else "empty",
                "created_at": now,
            })
        
    except DuplicateKeyError:
        existing = await search_jobs.find_by_hash(jobs_collection, query_hash)
        if existing:
            return {"status": "ok", "job_id": existing["_id"]}
        raise

    if result:
        results_collection = get_collection(lang, COLLECTION_RESULTS)
        await search_jobs.insert_results(results_collection,
            [{"job_id": job_id, "result": res, "created_at": now} for res in result],
        )

    return {"status": "ok", "job_id": job_id}


async def add_glossing(lang: str, doc_id: str):
    oid = _to_object_id(doc_id)
    if oid is None:
        return None

    collection = get_collection(lang, COLLECTION_SENT)
    return await collection.find_one({"_id": oid},
        projection={"segmented_text": 1, "glossed_text": 1})

async def return_dictionary(lang: str):
    collection = get_collection(lang, COLLECTION_DICT)
    return await collection.find({}).to_list(length=None)

async def return_letter_list(lang: str, letter: str):
    collection = get_collection(lang, COLLECTION_DICT)
    cursor = collection.find({"first_letter": letter.capitalize()})
    return await cursor.to_list(length=None)


async def return_group_by_id(lang: str, doc_id: str):
    """Страница значения: по _id леммы находим её перевод,
    затем возвращаем все леммы с этим же переводом (все слова одного значения)."""
    oid = _to_object_id(doc_id)
    if oid is None:
        return None

    collection = get_collection(lang, COLLECTION_DICT)
    anchor = await collection.find_one({"_id": oid})
    if anchor is None:
        return None

    translation = anchor.get("translation")
    if not translation:
        # Иначе find({"translation": None}) вернёт все леммы без перевода.
        return {"translation": translation, "documents": [anchor]}

    documents = await collection.find({"translation": translation}).to_list(length=None)
    return {"translation": translation, "documents": documents}


async def return_results(lang: str, job_id: str, offset: int = 0, limit: int = 20):
    """Возвращает страницу результатов или None, если джоб не найден.

    Сериализацию и коды ответа делает слой API — сервис про HTTP не знает.
    """
    job = await get_collection(lang, COLLECTION_JOB).find_one({"_id": job_id})
    if not job:
        return None

    collection = get_collection(lang, COLLECTION_RESULTS)
    total = await collection.count_documents({"job_id": job_id})
    docs = await collection.find({"job_id": job_id}).skip(offset).limit(limit).to_list(length=limit)
    return {"results": [doc["result"] for doc in docs if "result" in doc], "length": total}
