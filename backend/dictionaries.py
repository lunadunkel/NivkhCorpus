QUERY2DB = {'pos[]': 'POS', 'case[]': 'Case', 'nountype[]': 'NounType',
            'clusivity[]': 'Clusivity', 'verbform[]': 'VerbForm',
            'tense[]': 'Tense', 'aspect[]': 'Aspect', 
            'person[]': 'Person[word]',
            'number[]': 'Number[word]',
            'mood[]': 'Mood', 'misc[]': 'misc[]'}

ONLY4DB = {'person[]': 'Person[word]',
            'number[]': 'Number[word]'}

MISC = {

        'misc[]': {
            'caus': 'Voice=Caus',
            'aux': 'VerbType=Aux',
            'coord': 'Coordinating=Yes',
            'evid': 'Evident=Nfh',
            'neg': 'Polarity=Neg',
            'dim': 'Degree=Dim',
            'add': 'Add=Yes',
            'q': 'Question=Yes',
            'emph': 'Emphatic=Yes',
            'coll': 'NumType=Collective',
            'class': 'Classifier=Yes',
            'refl': 'Reflex=Yes',
            'indef': 'Definite=Ind',
            'rec': 'Reciprocal=Yes',
            'foc': 'Focus=Yes'
        }
}


dictionary_pipeline = [
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
        "rus": 1
    }},
    
    {"$sort": {"word": 1}}
]

# GRAMMAR_DICT = {"nfh": "Evident=Nfh", "caus": "Voice=Caus", 
#                            "ind": "Definite=Ind", "neg": "Polarity=Neg",
#                            "fut": "Tense=Fut", "dim": "Degree=Dim",
#                            "class": "Classifier=Yes", "pred": "Predicative=Yes",
#                            "foc": "Focus=Yes", "emph": "Emphatic=Yes",
#                            "qu": "Question=Yes", "coord": "Coordinating=Yes",
#                            "refl": "Reflex=Yes", "rec": "Reciprocal=Yes",
#                            "conces": "Conces=Yes", "add": "Add=Yes",
#                            "coll": "NumType=Collective", "aux": "VerbType=Aux",
#                            'conv': 'Conv'
# }