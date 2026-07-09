import os
from dotenv import load_dotenv
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["corpus"]

def get_collection(name: str):
    return db[name]

async def ping_db():
    return await db.list_collection_names()
