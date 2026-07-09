import argparse
import asyncio
import json
import string
from backend.core.dictionaries import dictionary_pipeline
from backend.mongodb.repositories.database import get_collection
from backend.mongodb.repositories.sentences_repo.insert_data import drop_collection

collection = get_collection('sentences')
dictionary = get_collection('dictionary')

parser = argparse.ArgumentParser(description="Получение словника")
parser.add_argument("-d", "--drop_collection", type=bool, default=False, help="Нужно ли удалить существующую коллекцию (по дефолту нет)")
args = parser.parse_args()

USED_WORDS = set()
translator = str.maketrans('', '', string.punctuation)

def decapitalize(word):
    new_word = word['lemma'].lower()
    new_word = new_word.translate(translator)
    if new_word in USED_WORDS:
        return
    
    USED_WORDS.add(word['lemma'].lower())
    if word['lemma'] == 'NaN':
        return
    if word['lemma'].istitle() and word['translation'].istitle():
        return 
    return {'lemma': new_word,
            'translation': word['translation'].lower(),
            'POS': word['POS'],
            "ex": word['text'],
            'tr': word['rus']}


async def main():
    results = await collection.aggregate(dictionary_pipeline).to_list()
    words_dict = []
    for item in results:
        new_item = decapitalize(item)
        if new_item:
            words_dict.append(new_item)

    if args.drop_collection:
        await drop_collection(dictionary)
    try:
        result = await dictionary.insert_many(words_dict)
        print(f"Inserted {len(result.inserted_ids)} documents.")
    except Exception as e:
        print(f"Error: {e}")

    # with open("words_aggregated.json", "w", encoding="utf-8") as f:
    #     json.dump(words_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(main())