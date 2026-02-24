from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from get_database import get_database
from backend.dictionaries import GRAMMAR_DICT

QUERY2DB = {'number[]': 'Number', 'pos[]': 'POS',
            'case[]': 'Case', 'number[]': 'Number',
            'person[]': 'Person', 'aspect[]': 'Aspect',
            'categories[]': 'Categories', 'verbform[]': 'Verbform',
            'clusivity[]': 'Clusivity', 'nountype[]': 'Nountype'}

@dataclass
class OriginalQuery:
    language: str = 'niv'
    search_type: str = 'wordform'
    input_word: Optional[str] = None
    gram_feats: Optional[dict] = None
    add_feats: Optional[dict] = None

class QueryBuilder:
    def __init__(self, query: list):
        self.queries = []
        language = query[0]['language-select']

        for num, q in enumerate(query):
            value = str(num) if num != 0 else '' 
            gram_feats, add_feats = dict(), dict()
            input_word = None
            search_type = 'wordform' 

            if q.get([f'search_type{value}']):
                search_type = q[f'search_type{value}']
                search_type = 'token' if search_type == 'wordform' else search_type

            if query[num].get([f'input_word{value}']):
                input_word = q[f'input_word{value}']

            if additional := query[num].get([f'additional[]'], None):
                if isinstance(additional, list):
                    for add in additional:
                        key, value = GRAMMAR_DICT[add].split('=')
                        add_feats[key] = value
                elif isinstance(additional, str):
                    key, value = GRAMMAR_DICT[additional].split('=')
                    add_feats[key] = value
            
            for key, db_key in QUERY2DB.items():
                if value := q.get(key, None):
                    gram_feats[db_key] = value
                
            self.queries.append(OriginalQuery(language=language,
                                   search_type=search_type,
                                   input_word=input_word,
                                   gram_feats=gram_feats,
                                   add_feats=add_feats))

# @dataclass
# class QueryBuilder:
#     filters: List[Dict[str, Any]] = field(default_factory=list)
#     requires_aggregate: bool = False

#     def lemma_match(self, word: str):
#         self.filters.append({"tokens.lemma": word})

#     def wordform_match(self, word):
#         query = {"tokens.lemma": f"{word}"}
#         QUERY.append(query)

#     def disjunction_query(self, tag: str, options: List):
#         field = f"tokens.tagsets.{tag}"
#         query = {field: {'$in': options}}
#         QUERY.append(query)  

#     def token_order(self, before: str, after: str):
#         self.requires_aggregate = True
#         self.before = before
#         self.after = after

db = get_database()

sentences_collection = db['sentences']

QUERY = []

PROJECTION = {
    "_id": 1,
    "tokens.$": 1,
    "russian_text": 1,
    "text": 1
}

# def lemma_match(word):
#     query = {"tokens.lemma": f"{word}"}
#     QUERY.append(query)

# def wordform(word):
#     query = {"tokens.lemma": f"{word}"}
#     QUERY.append(query)

# def disjunction_query(tag: str, options: List):
#     field = f"tokens.tagsets.{tag}"
#     query = {field: {'$in': options}}
#     QUERY.append(query)    


# lemma_match('нивх')
# disjunction_query('POS', ["NOUN", "VERB"])
# output = sentences_collection.find_one({'$and': QUERY}, PROJECTION)
# assert isinstance(output, dict)
# print(output)