import os
from dotenv import load_dotenv
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
load_dotenv()
USER = os.getenv('MONGO_USER')
PASSWORD = os.getenv('MONGO_PASSWORD')

CONNECTION_STRING = f"mongodb://{USER}:{PASSWORD}@localhost:27017/?authSource=admin&readPreference=primary&ssl=false"

client = AsyncIOMotorClient(CONNECTION_STRING)
db = client["nivkh_corpus"]

def get_collection(name: str):
    return db[name]
