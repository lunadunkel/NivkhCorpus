from motor.motor_asyncio import AsyncIOMotorCollection
from backend.core.config import COLLECTION_JOB, COLLECTION_RESULTS
from backend.db.database import get_collection

async def find_by_hash(collection: AsyncIOMotorCollection, query_hash: str):
    return await collection.find_one({"query_hash": query_hash})

async def insert_results(collection: AsyncIOMotorCollection, docs: list[dict]):
    await collection.insert_many(docs)

async def save(collection: AsyncIOMotorCollection, doc: dict):
    await collection.insert_one(doc)

async def get_by_id(collection: AsyncIOMotorCollection, job_id: str):
    return await collection.find_one({"_id": job_id})