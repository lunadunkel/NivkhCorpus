import argparse
import asyncio
import string
from backend.core.config import CORPORA
from backend.db.database import get_collection
from backend.db.repositories.dictionary_repo.get_alphabet import get_pipeline_by_lang
from backend.db.repositories.sentences_repo.insert_data import drop_collection

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
    return {'first_letter': word['first_letter'],
            'lemma': new_word,
            'translation': word['translation'].lower(),
            'POS': word['POS'],
            "ex": word['text'],
            'tr': word['rus']}


async def main():
    lang = args.language
    if lang not in CORPORA:
        raise ValueError(f"Language \"{lang}\" is not present in current version of DB. Currently avaliable options: {','.join(CORPORA.keys())}")
    collection = get_collection(lang, 'sentences')
    dictionary = get_collection(lang, 'dictionary')
    
    pipeline = get_pipeline_by_lang(lang)
    results = await collection.aggregate(pipeline).to_list()

    words_dict = []
    for item in results:
        new_item = decapitalize(item)
        if new_item:
            words_dict.append(new_item)

    if args.drop_collection:
        await drop_collection(dictionary)
    try:
        result = await dictionary.insert_many(words_dict)
        await dictionary.create_index([("first_letter", 1)])
        print(f"Inserted {len(result.inserted_ids)} documents.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Получение словника")
    parser.add_argument("-l", "--language", required=True, type=str, help="Выбрать корпус языка")
    parser.add_argument("-d", "--drop_collection", type=bool, default=False, help="Нужно ли удалить существующую коллекцию (по дефолту нет)")
    args = parser.parse_args()
    asyncio.run(main())