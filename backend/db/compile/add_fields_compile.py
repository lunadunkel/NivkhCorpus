from typing import Optional

from backend.db.compile.process_query import OriginalQuery
from backend.db.compile.render import render_expr


class AddFieldsCompiler:
    """Этап $addFields: индексы токенов, которые надо подсветить."""

    def __init__(self, query: list[OriginalQuery]):
        self.query = query
        self.fields_query = self.compile()

    def _build_single_add_fields(self, oq: OriginalQuery, fields: dict) -> dict:
        conditions = render_expr(oq.conditions)
        if not conditions:
            return fields

        mapping = {
            "$map": {
                "input": {
                    "$filter": {
                        "input": "$tokens",
                        "as": "x",
                        "cond": {"$and": conditions},
                    }
                },
                "as": "x",
                "in": "$$x.idx",
            }
        }

        if "final_indexes" not in fields:
            fields["final_indexes"] = {"$setUnion": []}
        fields["final_indexes"]["$setUnion"].append(mapping)

        return fields

    def compile(self) -> Optional[dict]:
        add_fields: dict = {}

        for q in self.query:
            add_fields = self._build_single_add_fields(q, add_fields)

        return {"$addFields": add_fields} if add_fields else None
