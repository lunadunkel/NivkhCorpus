import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)

def get_collection(lang: str, name: str):
    return client[lang][name]

async def ping_db():
    return await client.list_databases()
