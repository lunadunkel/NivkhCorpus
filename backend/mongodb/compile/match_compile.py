from typing import Dict, List, cast

from backend.mongodb.process_query import OriginalQuery


class MatchQueryCompiler:
    """Класс для создания match-query в mongo по обработанном запросу пользователя"""
    def __init__(self, query: List[OriginalQuery]):
        self.query = query
        self.match_query = self.compile()

    def _word_compile_match(self, oq: OriginalQuery) -> dict:
        """Создает mongodb match запрос на основе введенного пользователям слова 
        Args:
            oq (OriginalQuery): предобработанный запрос
        """
        language = oq.language # language
        search_type = oq.search_type # wordform/lemma search

        base_type, sub_type = 'tokens', search_type
        basic_query = oq.input_word # input word
        if language == 'russian': 
            if search_type == 'token':
                # based on wordform  –> different type of query
                base_type = 'russian_text'
                sub_type = None
                basic_query = {"$regex": basic_query, "$options": "i"}
            else:
                # based on lemma = based on lemma translation
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
        """Создает mongodb match запрос на основе введенных пользователям граммем 
        Args:
            oq (OriginalQuery): предобработанный запрос
            inter_query (dict, Optional): обработанный запрос по слову
        """
        if not inter_query:
            inter_query['tokens'] = dict()
            inter_query['tokens']['$elemMatch'] = dict()

        gram_feats = cast(Dict[str, str], oq.gram_feats)
        sub_type = 'tagsets'
        for key, value in gram_feats.items():
            # key = gram category / value = its value
            # forming query for each input grammatical/additional features
            basic_query = value
            if isinstance(value, list):
                # if a multiple-choice gramm –> using $in operator
                basic_query = {f'$in': value}
            inter_query['tokens']['$elemMatch'][f'{sub_type}.{key}'] = basic_query
        return inter_query

    def compile(self) -> dict:
        queries = []
        for q in self.query:
            inter_query = dict()
            if q.input_word is not None:
                # query based on input word
                inter_query = self._word_compile_match(q)
            if q.gram_feats is not None:
                # query based on grammatical/additional features
                inter_query = self._grammar_compile(q, inter_query)
            queries.append(inter_query)
        if len(queries) > 1:
            return {"$match": {'$and': queries}}
        return {"$match": queries[0]}