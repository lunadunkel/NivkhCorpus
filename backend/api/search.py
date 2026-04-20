from fastapi import APIRouter, Request
from backend.services import search_service

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/")
async def search(request: Request):
    query = await request.json()
    return await search_service.search(query)