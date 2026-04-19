from typing import Optional
from backend.mongodb.compile.match_compile import MatchQueryCompiler
from backend.mongodb.process_query import OriginalQuery

    
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
        """ Построения условия для каждого слова отдельно"""
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