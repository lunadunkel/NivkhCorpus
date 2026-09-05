import asyncio
import argparse
import os
from backend.core.config import CORPORA
from backend.db.database import get_collection
from backend.db.repositories.sentences_repo.process_json import Json2MongoProcessing


async def drop_collection(collection):
    await collection.drop()


async def main():
    preprocessing = Json2MongoProcessing(DATA_PATH)
    lang = args.language
    if lang not in CORPORA:
        raise ValueError(f"Language \"{lang}\" is not present in current version of DB. Currently avaliable options: {','.join(CORPORA.keys())}")
    collection = get_collection(lang, 'sentences')
    if args.drop_collection:
        await drop_collection(collection)
    for file in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, file)

        if file_path.endswith('json'):
            file_data = preprocessing.process_json(file_path)

            try:
                result = await collection.insert_many(file_data)
                print(f"Inserted {len(result.inserted_ids)} documents.")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Добавление предложений в корпус")
    parser.add_argument("-p", "--path", type=str, help="Путь к данным", required=True)
    parser.add_argument("-l", "--language", type=str, help="Язык корпуса", required=True)
    parser.add_argument("-d", "--drop_collection", type=bool, default=False, help="Нужно ли удалить существующую коллекцию (по дефолту нет)")
    args = parser.parse_args()
    DATA_PATH = args.path
    asyncio.run(main())