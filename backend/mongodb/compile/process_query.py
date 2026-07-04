from dataclasses import dataclass
from typing import Any, Dict, Optional
from backend.dictionaries import MISC, ONLY4DB, QUERY2DB

@dataclass
class OriginalQuery:
    language: str = 'niv'
    search_type: str = 'lemma'
    input_word: Optional[str] = None
    gram_feats: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

class QueryBuilder:
    def __init__(self, query: list):
        self.language = query[0]['language-select']
        self.queries = self.process_queries(query)
    
    def extract_gram_feats(self, query: dict) -> Dict:
        feats = {}
        for ui_key, db_key in QUERY2DB.items():

            if value := query.get(ui_key, None):
                if feature := MISC.get(ui_key, None):
                    if isinstance(value, list):
                        for val in value:
                            db_key, value = feature[val].split('=')
                            feats[db_key] = val
                    else:
                        db_key, value = feature[value].split('=')  
                        feats[db_key] = value

        person_obj = query.get('person_obj[]')
        clobj = query.get('clobj')
        clpos = query.get('clpos')

        if person_obj or clobj or clpos:
            feats['PersonObject'] = {
                'person': person_obj,
                'clobj': bool(clobj),
                'clpos': bool(clpos)
            }
        return feats
    
    def process_queries(self, query: list) -> list:
        queries = []
        for q in query:
            search_type = q.get('search-type')
            input_word = q.get('input_word') or None

            gram_feats = self.extract_gram_feats(q)
            if not gram_feats:
                gram_feats = None
                
            queries.append(OriginalQuery(language=self.language,
                                   search_type=search_type,
                                   input_word=input_word,
                                   gram_feats=gram_feats))
        return queries