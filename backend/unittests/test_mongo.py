from typing import Optional

import pytest

from backend.mongodb.create_query import AggregatePipeline
from backend.mongodb.process_query import OriginalQuery


# def make_query(word: str, gram: Optional[dict] = None):
#     return [OriginalQuery(
#         language="niv",
#         search_type="token",
#         input_word=word,
#         gram_feats=gram or {"VerbForm": "Conv"},
#     )]

# class QueryMaker:
#     def __init__(self, language, search_type, **kwargs):
#         self.language = language
#         self.search_type = search_type
#         self.additional = {key: value for key, value in kwargs.items()}

#     # def 

# def get_stage(pipeline, stage_name):
#     for stage in pipeline:
#         if stage_name in stage:
#             return stage[stage_name]
#     raise AssertionError(f"{stage_name} not found in pipeline")


# @pytest.mark.parametrize("word, gram",
#         [
#             ("ӿар", {"VerbForm": "Conv"})
#         ],
#     )
class TestSingleQuery:
    # def test_match_stage(word, gram):
    #     query = make_query(word, gram)
    #     pipeline = AggregatePipeline(query).aggregate()

    #     match = get_stage(pipeline, "$match")
    #     elem = match["tokens"]["$elemMatch"]

    #     assert elem["token"] == word

    #     for key, value in gram.items():
    #         assert elem[f"tagsets.{key}"] == value


    def test_nivkh_wordform(self):
        query = [OriginalQuery(language='niv',
                              search_type='token',
                              input_word='ӿар',
                              gram_feats={'VerbForm': 'Conv'})]

        match_stage = {
            "$match": {
                "tokens": {
                    "$elemMatch": {
                        "token": "ӿар",
                        "tagsets.VerbForm": "Conv"
                        }
                    }
                }
            }
        
        add_fields_stage = {"$addFields": {
            "final_indexes": {
                "$setUnion": [
                    {"$map": {
                        "input": {
                            "$filter": {
                                "input": "$tokens",
                                "as": "x",
                                "cond": {
                                    "$and": [
                                        {
                                            "$eq": ["$$x.token", "ӿар"]
                                            },
                                        {
                                            "$eq": ["$$x.tagsets.VerbForm",
                                                    "Conv"]
                                            }
                                        ]
                                    }
                                }
                            },
                            "as": "x",
                            "in": "$$x.idx"
                        }
                    }
                    ]
                }
        }   }


        project = {"$project": {
                "_id": 1,
                "russian_text": 1,
                "text": 1,
                "final_indexes": 1
            }
        }

        aggregate_compiler = AggregatePipeline(query)
        aggregation = aggregate_compiler.aggregate()

        assert aggregation[0] == match_stage
        assert aggregation[1] == add_fields_stage
        assert aggregation == [match_stage, add_fields_stage, project]
        
        
