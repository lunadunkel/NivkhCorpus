from backend.core.config import COLLECTION_JOB
from backend.mongodb.repositories.database import get_collection

async def find_by_hash(query_hash):
    collection = get_collection(COLLECTION_JOB)
    return await collection.find_one({"query_hash": query_hash})

async def save(doc):
    collection = get_collection(COLLECTION_JOB)
    await collection.insert_one(doc)

async def get_by_id(job_id):
    collection = get_collection(COLLECTION_JOB)
    return await collection.find_one({"_id": job_id})