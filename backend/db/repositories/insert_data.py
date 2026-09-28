import asyncio
import argparse
import os
from pathlib import Path

from pymongo.errors import BulkWriteError

from backend.core.config import CORPORA
from backend.db.database import get_collection
from backend.db.repositories.sentences_repo.process_json import Json2MongoProcessing


async def drop_collection(collection):
    await collection.drop()


async def main():
    lang = args.language
    if lang not in CORPORA:
        raise ValueError(f"Язык \"{lang}\" отсутствует в БД. Доступные корпуса: {','.join(CORPORA.keys())}")

    corpus = CORPORA[lang]
    if corpus.ingest is None:
        raise ValueError(f"В corpora/{lang}.yaml нет секции ingest")

    preprocessing = Json2MongoProcessing(Path(DATA_PATH), corpus.ingest.model_dump(), corpus.id)
    collection = get_collection(lang, 'sentences')
    if args.drop_collection:
        await drop_collection(collection)

    for file in sorted(os.listdir(DATA_PATH)):
        if not file.endswith('.json'):
            continue

        file_data = preprocessing.process_json(file)
        try:
            result = await collection.insert_many(file_data, ordered=False)
            print(f"{file}: inserted {len(result.inserted_ids)} documents.")
        except BulkWriteError as e:
            # _id детерминирован, поэтому повторная загрузка без -d упирается в дубли
            skipped = len(e.details["writeErrors"])
            print(f"{file}: inserted {e.details['nInserted']}, skipped {skipped} (already in collection or write error)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Добавление предложений в корпус")
    parser.add_argument("-p", "--path", type=str, help="Путь к данным", required=True)
    parser.add_argument("-l", "--language", type=str, help="Язык корпуса", required=True)
    parser.add_argument("-d", "--drop_collection", type=bool, default=False, help="Нужно ли удалить существующую коллекцию (по дефолту нет)")
    args = parser.parse_args()
    DATA_PATH = args.path
    asyncio.run(main())