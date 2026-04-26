import pprint
from datetime import datetime, timezone
import subprocess
import sys
import asyncio
from typing import Dict, Optional, Tuple
import uuid
from backend.mongodb.compile.aggregation_compile import AggregatePipeline
from backend.mongodb.repositories.database import get_collection
from backend.mongodb.compile.process_query import QueryBuilder
from backend.mongodb.repositories.jobs_repo import search_jobs
from backend.mongodb.repositories.utils import make_hash
from backend.services.jsontoyaml import JsonToYaml
from backend.core.config import COLLECTION_SENT, EXTRACTOR_DIR, USE_DB


async def extractor_search(query):
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
    return {"status": "ok", "job_id": "1"}

async def run_search_db(query):
    collection = get_collection(COLLECTION_SENT)
    qb = QueryBuilder(query)
    aggregate_compiler = AggregatePipeline(qb.queries)
    aggregation = aggregate_compiler.aggregate()

    cursor = collection.aggregate(aggregation)
    result = await cursor.to_list(length=None)
    return result

async def search(query):
    if not USE_DB:
        return extractor_search(query)
    query_hash = make_hash(query)
    existing = await search_jobs.find_by_hash(query_hash)
    if existing:
        return {"status": "ok", "job_id": existing["_id"]}
    result = await run_search_db(query)
    job_id = str(uuid.uuid4())

    await search_jobs.save({
        "_id": job_id,
        "query_hash": query_hash,
        # "result": result,
        "created_at": datetime.now(timezone.utc)
    })

    results = [{'job_id': job_id, 'result': res, "created_at": datetime.now(timezone.utc)} for res in result]

    await search_jobs.insert_results(results)

    return {"status": "ok", "job_id": job_id}