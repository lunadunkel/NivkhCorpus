from backend.core.deps import get_corpus

def get_pipeline_by_lang(language: str):
    corpus = get_corpus(language)

    alphabet_letters = [{"cap": L, "low": L.lower()} for L in corpus.alphabet_order]

    DICT_PIPELINE = [
    {"$unwind": "$tokens"},
    
    {"$match": {
        "tokens.translation": {"$exists": True, "$nin": ["", None]}
    }},
    
    {"$group": {
        "_id": "$tokens.token",           
        "lemma": {"$first": "$tokens.lemma"},     
        "translation": {"$first": "$tokens.translation"},
        "POS": {"$first": "$tokens.tagsets.POS"},
        "text": {"$first": "$text"},
        "rus": {"$first": "$russian_text"},
    }},
    
    {"$project": {
        "_id": 0,
        "word": "$_id",
        "lemma": 1,
        "translation": 1,
        "POS": 1,
        "text": 1,
        "rus": 1,

        "first_letter": {
            "$reduce": {
                "input": alphabet_letters,
                "initialValue": "",
                "in": {
                    "$cond": [
                        {"$and": [
                            {"$eq": ["$$value", ""]},
                            {"$in": [
                                {"$substrCP": ["$_id", 0, {"$strLenCP": "$$this.cap"}]},
                                ["$$this.low", "$$this.cap"],
                            ]},
                        ]},
                        "$$this.cap",
                        "$$value",
                    ]
                }
            }
        }
    }},
    
    {"$sort": {"word": 1}}
]

    return DICT_PIPELINE


