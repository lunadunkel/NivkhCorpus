QUERY2DB = {'pos[]': 'POS', 'case[]': 'Case', 'nountype[]': 'NounType',
            'clusivity[]': 'Clusivity', 'verbform[]': 'VerbForm',
            'tense[]': 'Tense', 'aspect[]': 'Aspect', 
            'person[]': ['Person[subj]', 'Person'],
            'number[]': ['Number[subj]', 'Number'],
            'person_obj[]': 'Person[obj]', 'number_obj[]': 'Number[obj]', 
            'mood[]': 'Mood', 'verb[]': 'verb[]', 'misc[]': 'misc[]'}

ONLY4DB = {'person[]': 'Person[subj]',
            'number[]': 'Number[subj]'}

MISC: dict[str, dict] = {
        'verb[]': {
            'caus': 'Voice=Caus',
            'pred': 'Predicative=Yes',
            'aux': 'VerbType=Aux',
            'coord': 'Coordinating=Yes'
        },

        'misc[]': {
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