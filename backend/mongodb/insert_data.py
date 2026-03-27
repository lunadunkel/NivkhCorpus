import json
import os

from backend.core.config import JSON_DATA_PATH
from backend.mongodb.get_database import get_database
from backend.mongodb.preprocess_mongo import Json2MongoProcessing


db = get_database()
collection = db['sentences']

preprocessing = Json2MongoProcessing(JSON_DATA_PATH)

for file in os.listdir(JSON_DATA_PATH):
    file_path = os.path.join(JSON_DATA_PATH, file)
    if file_path.endswith('json'):
        file_data = preprocessing.process_json(file_path)
        try:
            result = collection.insert_many(file_data)
            print(f"Inserted {len(result.inserted_ids)} documents.")
        except Exception as e:
            print(f"An error occurred: {e}")
