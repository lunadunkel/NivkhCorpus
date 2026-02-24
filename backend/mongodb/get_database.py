import os
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()

def get_database():
    USER = os.getenv('MONGO_USER')
    PASSWORD = os.getenv('MONGO_PASSWORD')

    CONNECTION_STRING = f"mongodb://{USER}:{PASSWORD}@localhost:27017/?authSource=admin&readPreference=primary&ssl=false"

    client = MongoClient(CONNECTION_STRING)

    db = client['nivkh_corpus']
    return db
