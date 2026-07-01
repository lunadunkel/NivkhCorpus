from typing import Optional
from backend.mongodb.compile.match_compile import MatchQueryCompiler
from backend.mongodb.compile.process_query import OriginalQuery

    
class AddFieldsCompiler:
    """
    Класс для создания addFields-query в mongo по обработанном запросу пользователя
    """
    def __init__(self, query: list[OriginalQuery]):
        self.query = query
        self.fields_query = self.compile()
    
    def _get_person_fields(self, clobj: bool, clpos: bool, prefix: str = "tagsets"):
        fields = []

        if clobj:
            fields.append(f"{prefix}.Person[clobj]")
        if clpos:
            fields.append(f"{prefix}.Person[clpos]")

        return fields or [
            f"{prefix}.Person[clobj]",
            f"{prefix}.Person[clpos]"
        ]

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
            person_object = oq.gram_feats.get("PersonObject")

            for key, value in oq.gram_feats.items():
                if key == "PersonObject":
                    continue

                field = f"$$x.tagsets.{key}"

                conditions.append(
                    {"$in": [field, value]}
                    if isinstance(value, list)
                    else {"$eq": [field, value]}
                )

            if person_object:
                person = person_object["person"]

                fields = self._get_person_fields(
                    person_object["clobj"],
                    person_object["clpos"],
                    "$$x.tagsets"
                )

                if person:
                    operator = "$in" if isinstance(person, list) else "$eq"

                    if len(fields) == 1:
                        conditions.append(
                            {operator: [fields[0], person]}
                            if operator == "$eq"
                            else {"$in": [fields[0], person]}
                        )
                    else:
                        conditions.append({
                            "$or": [
                                (
                                    {"$eq": [field, person]}
                                    if operator == "$eq"
                                    else {"$in": [field, person]}
                                )
                                for field in fields
                            ]
                        })

                else:
                    exists_conditions = [
                        {
                            "$ne": [
                                {"$ifNull": [field, None]},
                                None
                            ]
                        }
                        for field in fields
                    ]

                    conditions.append(
                        exists_conditions[0]
                        if len(fields) == 1
                        else {"$or": exists_conditions}
                    )

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