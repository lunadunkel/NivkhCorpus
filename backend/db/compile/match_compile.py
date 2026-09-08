from typing import List

from backend.db.compile.process_query import OriginalQuery
from backend.db.compile.render import render_match


class MatchQueryCompiler:
    """Этап $match: какие предложения вернутся."""

    def __init__(self, query: List[OriginalQuery]):
        self.query = query
        self.match_query = self.compile()

    def compile(self) -> dict:
        queries = [render_match(q.conditions) for q in self.query]

        if len(queries) > 1:
            return {"$match": {"$and": queries}}
        return {"$match": queries[0]}
