from dataclasses import dataclass
from typing import Any, Dict, Optional
from backend.dictionaries import GRAMMAR_DICT, QUERY2DB

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
            if ui_key == 'additional[]':
                continue
            if value := query.get(ui_key):
                feats[db_key] = value
        return feats
    
    def extract_add_feats(self, query: dict, gram_feats: dict = {}) -> Dict:
        additional = query.get('additional[]')
        if not additional:
            return gram_feats

        if not isinstance(additional, list):
            additional = [additional]

        feats = {}
        for add in additional:
            key, value = GRAMMAR_DICT[add].split('=')
            feats[key] = value
        if feats:
            gram_feats.update(feats)
        return gram_feats
    
    def process_queries(self, query: list) -> list:
        queries = []
        for q in query:
            search_type = q.get('search-type')
            input_word = q.get('input_word') or None

            gram_feats = self.extract_gram_feats(q)
            gram_feats = self.extract_add_feats(q, gram_feats)
            if not gram_feats:
                gram_feats = None
                
            queries.append(OriginalQuery(language=self.language,
                                   search_type=search_type,
                                   input_word=input_word,
                                   gram_feats=gram_feats))
        return queries