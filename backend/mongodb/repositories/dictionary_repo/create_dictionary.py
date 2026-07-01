import argparse
import asyncio
import json
from backend.dictionaries import dictionary_pipeline
from backend.mongodb.repositories.database import get_collection

collection = get_collection('sentences')

parser = argparse.ArgumentParser(description="Получение словника")
parser.add_argument("-d", "--drop_collection", type=bool, default=False, help="Нужно ли удалить существующую коллекцию (по дефолту нет)")
args = parser.parse_args()

def decapitalize(word):
    if word['lemma'] == 'NaN':
        return {}
    if word['lemma'].istitle() and word['translation'].istitle():
        return {}
    return {word['lemma'].lower(): word['translation'].lower()}


async def main():
    results = await collection.aggregate(dictionary_pipeline).to_list()
    words_dict = dict()
    for item in results:
        words_dict.update(decapitalize(item))

    with open("words_aggregated.json", "w", encoding="utf-8") as f:
        json.dump(words_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(main())