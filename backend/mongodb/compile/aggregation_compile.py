from typing import List
from backend.mongodb.compile.add_fields_compile import AddFieldsCompiler
from backend.mongodb.compile.match_compile import MatchQueryCompiler
from backend.mongodb.process_query import OriginalQuery


class AggregatePipeline:
    def __init__(self, query: List[OriginalQuery]):
        self.query = query
    
    def _form_project(self, ) -> dict:
        """Внутренняя функция для написания проекции = поля, возвращаемые из БД"""
        project = {
                "_id": 1,
                "russian_text": 1,
                "text": 1,
                "final_indexes": 1,
                "author": '$metadata.author',
                "title": '$metadata.title_n'
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