from typing import Any, Dict, List, Optional, cast
# import pprint
from backend.mongodb.process_query import OriginalQuery


class MatchQueryCompiler:
    """
    Класс для создания match-query в mongo по обработанном запросу пользователя
    """
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
    
class AddFieldsCompiler:
    """
    Класс для создания addFields-query в mongo по обработанном запросу пользователя
    """
    def __init__(self, query: list[OriginalQuery]):
        self.query = query
        self.fields_query = self.compile()

    def _build_conditions(self, oq: OriginalQuery) -> list[dict]:
        """Внутренняя функция для написания условий на этапе addFields"""
        language = oq.language
        search_type = oq.search_type

        conditions = []

        if oq.input_word:
            if search_type == 'token':
                if language == "russian":
                    return conditions
                else:
                    conditions.append({"$eq": ["$$x.token", oq.input_word]})
            
            if search_type == 'lemma':
                if language == 'russian':
                    conditions.append({"$eq": ["$$x.translation", oq.input_word]})
                else:
                    conditions.append({"$eq": ["$$x.lemma", oq.input_word]})

        # граммемы
        if oq.gram_feats:
            for key, value in oq.gram_feats.items():
                field = f"$$x.tagsets.{key}"

                if isinstance(value, list):
                    conditions.append({"$in": [field, value]})
                else:
                    conditions.append({"$eq": [field, value]})
        
        return conditions

    def _build_single_add_fields(self, oq: OriginalQuery, fields_dictionary: dict) -> dict:
        """ Построения условия для каждого слова отдельного """
        conditions = self._build_conditions(oq)
        if not conditions:
            return fields_dictionary

        mapping = {"$map": {
                    "input": {
                        "$filter": {
                            "input": "$tokens",
                            "as": "x",
                            "cond": {"$and": conditions} 
                        }
                    },
                    "as": "x",
                    "in": "$$x.idx"
                }
            }

        
        # indices_set = {"$setUnion": []}
        if "final_indexes" not in fields_dictionary:
            fields_dictionary["final_indexes"] = {"$setUnion": []}
        fields_dictionary["final_indexes"]["$setUnion"].append(mapping)

        return fields_dictionary

    def compile(self) -> Optional[dict]:
        """ Основная функция написания условий в addFields"""
        add_fields = {}

        for q in self.query:
            add_fields = self._build_single_add_fields(q, add_fields)
        if add_fields:
            return {"$addFields": add_fields}
        return None

class AggregatePipeline:
    def __init__(self, query: List[OriginalQuery]):
        self.query = query
    
    def _form_project(self, ) -> dict:
        """Внутренняя функция для написания проекции = поля, возвращаемые из БД"""
        project = {
                "_id": 1,
                "russian_text": 1,
                "text": 1,
                "final_indexes": 1
            }

        return {'$project': project}
    
    def aggregate(self) -> list[dict]:
        """ Выполнение аггрегационного запроса из трех этапов: match, addFields, project"""
        match_compiler = MatchQueryCompiler(self.query)
        addfields_compiler = AddFieldsCompiler(self.query)

        aggregation = []

        aggregation.append(match_compiler.compile())
        fields_query = addfields_compiler.compile()
        if fields_query is not None:
            aggregation.append(fields_query)
        
        aggregation.append(self._form_project())
        
        return aggregation 



# # query = [{'language-select': 'nivkh', 'search-type': 'token', 'input_word': 'видь', 'added-gram-features': '', 'additional[]': 'foc'}]
# # query = [{'language-select': 'nivkh', 'search-type': 'lemma', 'input_word': 'ви', 
# #           'added-gram-features': '', 'number[]': ['Sing', 'Pl'], 'mood[]': 'Imp'},
# #           {'language-select': 'nivkh', 'search-type': 'lemma', 'input_word': '', 
# #            'added-gram-features': '', 'number[]': ['Sing']}]
# # query = [{'language-select': 'russian', 'search-type': 'token', 'input_word': 'мастерски', 'added-gram-features': ''}]
# # query = [{'language-select': 'nivkh', 'search-type': 'lemma', 'input_word': 'ӿо', 'added-gram-features': '', 'number[]': 'Sing'}, {'search-type': 'token', 'input_word': '', 'additional[]': 'refl'}]
# query = [{'language-select': 'russian', 'search-type': 'token', 'input_word': 'медведя', 'added-gram-features': ''}]
# db = get_database()
# collection = db['sentences']

# qb = QueryBuilder(query)

# aggregate_compiler = AggregatePipeline(qb.queries)

# aggregation = aggregate_compiler.aggregate()
# print(aggregation)
# result = collection.aggregate(aggregation)
# for res in result:
#     pprint.pprint(res)
#     break