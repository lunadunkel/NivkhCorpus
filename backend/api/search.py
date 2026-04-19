import uuid
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from backend.core.config import USE_DB
from backend.mongodb.compile.aggregation_compile import AggregatePipeline
from backend.mongodb.database import get_collection
from backend.mongodb.process_query import QueryBuilder
from backend.services.search_query import run_search, run_search_db

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/")
async def search(request: Request):
    query = await request.json()
    print(query)
    print(USE_DB)
    if not USE_DB:
        status = await run_search(query)
        if status['status'] == 'ok':
            return JSONResponse({"status": "ok", "job_id": "1"})
        return JSONResponse({"status": "bad", "job_id": "1"})
    result = await run_search_db(query)

    job_id = str(uuid.uuid4())

    collection = get_collection("sentences")
    await collection.insert_one({
        "_id": job_id,
        "query": query,
        "result": result
    })
    return {"status": "ok", "job_id": job_id}
    