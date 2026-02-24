from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from backend.services.search_query import run_search

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/")
async def search(request: Request):
    query = await request.json()
    status = await run_search(query)
    if status['status'] == 'ok':
        return JSONResponse({"status": "ok"})