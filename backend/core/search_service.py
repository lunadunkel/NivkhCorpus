from datetime import datetime, timezone
import re
import uuid
from bson import ObjectId
from backend.mongodb.compile.aggregation_compile import AggregatePipeline
from backend.mongodb.repositories.database import get_collection
from backend.mongodb.compile.process_query import QueryBuilder
from backend.mongodb.repositories.jobs_repo import search_jobs
from backend.mongodb.repositories.utils import make_hash
from backend.core.config import COLLECTION_SENT, COLLECTION_DICT


async def run_search_db(query):
    collection = get_collection(COLLECTION_SENT)
    qb = QueryBuilder(query)
    aggregate_compiler = AggregatePipeline(qb.queries)
    aggregation = aggregate_compiler.aggregate()
    print(aggregation)
    cursor = collection.aggregate(aggregation)
    result = await cursor.to_list(length=None)
    return result

async def search(query):
    query_hash = make_hash(query)
    existing = await search_jobs.find_by_hash(query_hash)
    if existing:
        return {"status": "ok", "job_id": existing["_id"]}
    result = await run_search_db(query)
    job_id = str(uuid.uuid4())

    await search_jobs.save({
        "_id": job_id,
        "query_hash": query_hash,
        "status": "empty" if not result else "done",
        "created_at": datetime.now(timezone.utc)
    })
    if result:
        results = [
            {'job_id': job_id, 'result': res, "created_at": datetime.now(timezone.utc)}
            for res in result
        ]
        await search_jobs.insert_results(results)

    return {"status": "ok", "job_id": job_id}

async def add_glossing(doc_id):
    collection = get_collection(COLLECTION_SENT)
    result = await collection.find_one({"_id": ObjectId(doc_id)}, projection={"segmented_text": 1, "glossed_text": 1})
    return result

async def return_dictionary():
    collection = get_collection(COLLECTION_DICT)
    cursor = collection.find({})
    documents = await cursor.to_list() 
    return documents

async def return_letter_list(letter):
    collection = get_collection(COLLECTION_DICT)

    pattern = '^' + re.escape(letter) + '(?![\u2019\u030c\u02C7])'
    cursor = collection.find({"lemma": {"$regex": pattern}})
    documents = await cursor.to_list() 
    return documents


async def return_group_by_id(doc_id):
    """Страница значения: по _id леммы находим её перевод,
    затем возвращаем все леммы с этим же переводом (все слова одного значения)."""
    collection = get_collection(COLLECTION_DICT)
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