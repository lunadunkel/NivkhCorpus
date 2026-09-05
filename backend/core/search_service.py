from datetime import datetime, timezone
import re
import uuid
from bson import ObjectId
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorCollection
from backend.core.config import COLLECTION_DICT, COLLECTION_JOB, COLLECTION_RESULTS, COLLECTION_SENT
from backend.db.database import get_collection
from backend.db.compile.process_query import QueryBuilder
from backend.db.compile.aggregation_compile import AggregatePipeline
from backend.db.repositories.jobs_repo import search_jobs
from backend.db.repositories.utils import clean, make_hash


async def run_search_db(collection: AsyncIOMotorCollection, query: list[dict]):
    qb = QueryBuilder(query)
    aggregate_compiler = AggregatePipeline(qb.queries)
    aggregation = aggregate_compiler.aggregate()
    cursor = collection.aggregate(aggregation)
    result = await cursor.to_list(length=None)
    return result

async def search(lang: str, query):
    collection = get_collection(lang, COLLECTION_SENT)
    query_hash = make_hash(query)
    existing = await search_jobs.find_by_hash(collection, query_hash)

    if existing:
        return {"status": "ok", "job_id": existing["_id"]}
    
    result = await run_search_db(collection, query)
    job_id = str(uuid.uuid4())

    job_collection = get_collection(lang, COLLECTION_JOB)

    await search_jobs.save(job_collection, {
        "_id": job_id,
        "query_hash": query_hash,
        "status": "empty" if not result else "done",
        "created_at": datetime.now(timezone.utc)
    })

    results_collection = get_collection(lang, COLLECTION_RESULTS)

    if result:
        results = [
            {'job_id': job_id, 'result': res, "created_at": datetime.now(timezone.utc)}
            for res in result
        ]
        await search_jobs.insert_results(results_collection, results)

    return {"status": "ok", "job_id": job_id}

async def add_glossing(lang: str, doc_id: str):
    collection = get_collection(lang, COLLECTION_SENT)
    result = await collection.find_one({"_id": ObjectId(doc_id)}, projection={"segmented_text": 1, "glossed_text": 1})
    return result

async def return_dictionary(lang: str):
    collection = get_collection(lang, COLLECTION_DICT)
    cursor = collection.find({})
    documents = await cursor.to_list() 
    return documents

async def return_letter_list(lang: str, letter: str):
    letter = letter.capitalize()
    collection = get_collection(lang, COLLECTION_DICT)
    cursor = collection.find({"first_letter": letter})
    documents = await cursor.to_list() 
    return documents

async def return_group_by_id(lang: str, doc_id: str):
    """Страница значения: по _id леммы находим её перевод,
    затем возвращаем все леммы с этим же переводом (все слова одного значения)."""
    collection = get_collection(lang, COLLECTION_DICT)
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return None
    anchor = await collection.find_one({"_id": oid})
    if anchor is None:
        return None
    translation = anchor.get("translation")
    cursor = collection.find({"translation": translation})
    documents = await cursor.to_list()
    return {"translation": translation, "documents": documents}

async def return_results(lang: str, job_id: str, offset: int = 0, limit: int = 20):
    job_exists = await get_collection(lang, COLLECTION_JOB).find_one({"_id": job_id})
    if not job_exists:
        return JSONResponse({"Error": "job not found"}, status_code=404)
    collection = get_collection(lang, COLLECTION_RESULTS)
    total = await collection.count_documents({"job_id": job_id})
    cursor = collection.find({"job_id": job_id}).skip(offset).limit(limit)
    docs = await cursor.to_list(length=limit)

    cleaned_results = [clean(doc['result']) for doc in docs]

    return JSONResponse({"results": cleaned_results, "length": total})