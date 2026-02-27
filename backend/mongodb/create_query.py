# TO-DO: переписать для aggregation части pipeline
# то, что сейчас формируется в MongoQueryCompiler

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, cast
from backend.mongodb.get_database import get_database
from backend.dictionaries import GRAMMAR_DICT, QUERY2DB


RUSSIAN_WORDFORM = False

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

class MongoQueryCompiler:
    def __init__(self, query: List[OriginalQuery]):
        self.query = query
        self.final_query = self.basic_compile()

    def _word_compile_match(self, oq: OriginalQuery) -> dict:
        language = oq.language
        search_type = oq.search_type

        base_type, sub_type = 'tokens', search_type
        basic_query = oq.input_word
        if language == 'russian': 
            if search_type == 'token':
                RUSSIAN_WORDFORM = True
                base_type = 'russian_text'
                sub_type = None
                basic_query = f'/{basic_query}/i'
            else:
                sub_type = 'translation'
        if sub_type is not None:
            query = {f'{base_type}':
                        {'$elemMatch':
                            {sub_type: basic_query}
                        }
                    }
        else:
            query = {f'{base_type}': basic_query}
        return query
    
    def _grammar_compile(self, oq: OriginalQuery, inter_query: dict = dict()) -> dict:
        if not inter_query:
            inter_query['tokens'] = dict()
            inter_query['tokens']['$elemMatch'] = dict()

        gram_feats = cast(Dict[str, str], oq.gram_feats)
        sub_type = 'tagsets'
        for key, value in gram_feats.items():
            basic_query = value
            if isinstance(value, list):
                basic_query = {f'$in': value}
            inter_query['tokens']['$elemMatch'][f'{sub_type}.{key}'] = basic_query
        return inter_query

    def basic_compile(self) -> list[dict]:
        queries = []
        for q in self.query:
            inter_query = dict()
            if q.input_word is not None:
                inter_query = self._word_compile_match(q)
            if q.gram_feats is not None:
                inter_query = self._grammar_compile(q, inter_query)
            queries.append(inter_query)
        return queries

class MongoAggregatePipeline:
    def __init__(self, queries: list[dict]):
        self.use_basic_project = True if len(queries) == 1 else False
        self.queries = queries
        self.project = self._form_project()
    
    def _form_project(self) -> dict[str, int]:
        project = {
                "_id": 1,
                "russian_text": 1,
                "text": 1
            }
        if RUSSIAN_WORDFORM: return project

        index_level = "tokens.$" if self.use_basic_project else "final_indexes"
        project[index_level] = 1
        return project



# query = [{'language-select': 'nivkh', 'search-type': 'token', 'input_word': 'видь', 'added-gram-features': '', 'additional[]': 'foc'}]
query = [{'language-select': 'nivkh', 'search-type': 'lemma', 'input_word': 'ви', 
          'added-gram-features': '', 'number[]': ['Sing', 'Pl'], 'mood[]': 'Imp'},
          {'language-select': 'nivkh', 'search-type': 'lemma', 'input_word': '', 
           'added-gram-features': '', 'number[]': ['Sing']}]
db = get_database()

# sentences_collection = db['sentences']

qb = QueryBuilder(query)
print(qb.queries[0].to_dict())
compiler = MongoQueryCompiler(qb.queries)
print(compiler.final_query)