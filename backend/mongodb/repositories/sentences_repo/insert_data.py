import asyncio
import argparse
import os
from backend.core.config import JSON_DATA_PATH
from backend.mongodb.repositories.database import get_collection
from backend.mongodb.repositories.sentences_repo.process_json import Json2MongoProcessing


parser = argparse.ArgumentParser(description="Добавление предложений в корпус")
parser.add_argument("-d", "--drop_collection", type=bool, default=False, help="Нужно ли удалить существующую коллекцию (по дефолту нет)")
args = parser.parse_args()

collection = get_collection('sentences')

async def drop_collection(collection):
    await collection.drop()


preprocessing = Json2MongoProcessing(JSON_DATA_PATH)

async def main():
    if args.drop_collection:
        await drop_collection(collection)
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