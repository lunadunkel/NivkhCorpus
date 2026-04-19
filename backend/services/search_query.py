import pprint
import subprocess
import sys
import asyncio
from backend.mongodb.compile.aggregation_compile import AggregatePipeline
from backend.mongodb.database import get_collection
from backend.mongodb.process_query import QueryBuilder
from backend.services.jsontoyaml import JsonToYaml
from backend.core.config import EXTRACTOR_DIR

async def run_search(query):
    JsonToYaml(query)
    await asyncio.to_thread(
        lambda: subprocess.run([
            sys.executable,
            "EX_tractor_1.4.py",
            "--rules", "24",
            "--dir_in", "Input/main",
            "--output_txt", "Output/search_result.txt",
            "--verbosity", "0",
            "--output_csv", "Output/search_result.csv",
            "--csv_verbosity", "1"
        ], cwd=EXTRACTOR_DIR, check=True)
    )
    print(query)
    return {"status": "ok"}

async def run_search_db(query):
    collection = get_collection("sentences")

    qb = QueryBuilder(query)
    print(qb.queries)
    aggregate_compiler = AggregatePipeline(qb.queries)
    aggregation = aggregate_compiler.aggregate()

    print("QUERY:", query)
    print("PIPELINE:", aggregation)

    cursor = collection.aggregate(aggregation)
    result = await cursor.to_list(length=None)
    for res in result:
        pprint.pprint(res)
        break
    
    return result