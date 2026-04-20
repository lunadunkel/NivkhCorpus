import asyncio
import os
from backend.core.config import JSON_DATA_PATH
from backend.mongodb.repositories.database import get_collection
from backend.mongodb.repositories.sentences_repo.process_json import Json2MongoProcessing

collection = get_collection('sentences')
preprocessing = Json2MongoProcessing(JSON_DATA_PATH)

async def main():
    for file in os.listdir(JSON_DATA_PATH):
        file_path = os.path.join(JSON_DATA_PATH, file)

        if file_path.endswith('json'):
            file_data = preprocessing.process_json(file_path)

            try:
                result = await collection.insert_many(file_data)
                print(f"Inserted {len(result.inserted_ids)} documents.")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())