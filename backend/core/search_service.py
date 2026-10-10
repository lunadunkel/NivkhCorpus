from shlex import quote
from typing import Any
import uuid
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi.responses import JSONResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError

from backend.core.config import COLLECTION_DICT, COLLECTION_JOB, COLLECTION_RESULTS, COLLECTION_SENT
from backend.core.it_text import format_grammar
from backend.models.corpus import CorpusConfig
from backend.db.compile.aggregation_compile import AggregatePipeline
from backend.db.compile.process_query import OriginalQuery, QueryBuilder, queries_from_doc, queries_to_doc
from backend.db.database import get_collection
from backend.db.repositories import search_jobs
from backend.db.repositories.utils import clean, make_hash


def attachment(filename: str) -> dict:
    return {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"}

def _to_object_id(doc_id: str) -> ObjectId | None:
    try:
        return ObjectId(doc_id)
    except (InvalidId, TypeError):
        return None


async def run_search_db(corpus: CorpusConfig, collection: AsyncIOMotorCollection, queries: list[OriginalQuery]):
    aggregation = AggregatePipeline(queries, corpus.search).aggregate()
    cursor = collection.aggregate(aggregation)
    return await cursor.to_list(length=None)

async def save_results(lang: str, job_id: str, result: list[dict]):
    now = datetime.now(timezone.utc)
    collection = get_collection(lang, COLLECTION_RESULTS)
    results = [{"_id": f"{job_id}:{i}",
            "job_id": job_id,
            "idx": i,
            "result": res, "created_at": now}
           for i, res in enumerate(result)]
    await search_jobs.insert_results(collection, results)

async def search(corpus: CorpusConfig, query):
    lang = corpus.id
    jobs_collection = get_collection(lang, COLLECTION_JOB)
    sent_collection = get_collection(lang, COLLECTION_SENT)

    queries = QueryBuilder(corpus, forms=query).queries
    ir = queries_to_doc(queries)
    query_hash = make_hash(ir)
    
    existing = await search_jobs.find_by_hash(jobs_collection, query_hash)
    results = await search_jobs.find_by_hash(jobs_collection, query_hash)
    if existing:
        return {"status": "ok", "job_id": existing["_id"]}

    result = await run_search_db(corpus, sent_collection, queries)
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    try:
        await search_jobs.save(jobs_collection, {
                "_id": job_id,
                "query_hash": query_hash,
                "form": query,   # для восстановления формы в интерфейсе
                "status": "done" if result else "empty",
                "ir": ir,        # по нему ищем при переходе по ссылке
            })
        
    except DuplicateKeyError:
        existing = await search_jobs.find_by_hash(jobs_collection, query_hash)
        if existing:
            return {"status": "ok", "job_id": existing["_id"]}
        raise

    if result:
        await save_results(lang, job_id, result)

    return {"status": "ok", "job_id": job_id}


async def add_glossing(lang: str, doc_id: str):
    candidates: list = [doc_id]
    oid = _to_object_id(doc_id)
    if oid is not None:
        candidates.append(oid)

    collection = get_collection(lang, COLLECTION_SENT)
    return await collection.find_one({"_id": {"$in": candidates}},
        projection={"segmented_text": 1, "glossed_text": 1})

async def return_dictionary(lang: str):
    collection = get_collection(lang, COLLECTION_DICT)
    return await collection.find({}).to_list(length=None)

async def return_letter_list(lang: str, letter: str):
    collection = get_collection(lang, COLLECTION_DICT)
    cursor = collection.find({"first_letter": letter.capitalize()})
    return await cursor.to_list(length=None)

async def get_form(corpus: CorpusConfig, job_id: str) -> list[dict] | None:
    job = await get_collection(corpus.id, COLLECTION_JOB).find_one({"_id": job_id}, projection={"form": 1})
    return job.get("form") if job else None

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


async def return_results(corpus: CorpusConfig, job_id: str, offset: int = 0, limit: int = 20):
    """Возвращает страницу результатов или None, если джоб не найден. Сериализацию и коды ответа делает слой API — сервис про HTTP не знает."""

    lang = corpus.id
    job = await get_collection(lang, COLLECTION_JOB).find_one({"_id": job_id})
    if not job:
        return None

    queries = queries_from_doc(job["ir"])
    collection = get_collection(lang, COLLECTION_RESULTS)
    total = await collection.count_documents({"job_id": job_id})
    if total == 0 and job["status"] == "done":
        result = await run_search_db(corpus, get_collection(lang, COLLECTION_SENT), queries)
        await save_results(lang, job_id, result)
        total = len(result)
    docs = await collection.find({"job_id": job_id}).sort("idx", 1).skip(offset).limit(limit).to_list(length=limit)
    return {"results": [doc["result"] for doc in docs if "result" in doc], "length": total,
           "queries": [format_grammar(q.conditions) for q in queries]}

async def get_meta(corpus: CorpusConfig, job_id: str, condition: dict[str, list[str]], 
                   sort: str = "default", offset: int = 0, limit: int = 20):
    lang = corpus.id
    collection = get_collection(lang, COLLECTION_RESULTS)
    SORTS = {
        "default": [("idx", 1)],
        "old": [("result.date", 1), ("idx", 1)],
        "new": [("result.date", -1), ("idx", 1)],
    }
    query: dict[str, Any[str|list]] = {"job_id": job_id}
    for field, values in condition.items():
        if not values:
            continue
        mapping = {label: key for key, label in corpus.meta[field].items()}
        query[f"result.{field}"] = {"$in": [mapping[v] for v in values]}
    total = await collection.count_documents(query)
    docs = await collection.find(query).sort(SORTS[sort]).skip(offset).limit(limit).to_list(length=limit)
    return {"results": [doc["result"] for doc in docs if "result" in doc], "length": total}

async def copy_example(corpus: CorpusConfig, example_id: str):
    lang = corpus.id
    collection = get_collection(lang, COLLECTION_SENT)
    translation = corpus.search.sentence_text_field
    project = {"segmented_text": 1, translation: 1, "glossed_text": 1, 
               "metadata.author": 1, "metadata.title_r": 1, "metadata.source": 1}

    filename = f"results.{format}"

    result = await collection.find_one({"_id": example_id}, project)
    if result:
        example = f"""{result['metadata']['author']}: {result['metadata']['title_r']}
{'\t'.join(result['segmented_text'].split())}
{'\t'.join(result['glossed_text'].split())}
{result[translation]}
[{result['metadata']['source']}]
"""
        return example
    return ''