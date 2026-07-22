from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from backend.core import search_service
from backend.mongodb.repositories.utils import clean

router = APIRouter(prefix="/{lang}/search", tags=["Search"])

@router.post("/")
async def search(request: Request):
    query = await request.json()
    return await search_service.search(query)

@router.post("/doc_id={doc_id}")
async def search_id(doc_id: str):
   result = await search_service.add_glossing(doc_id)
   if result is not None:
      return {"segmentation": result['segmented_text'], "glossing": result['glossed_text']}
   return JSONResponse({"error": "not found"}, status_code=404)

@router.get("/dictionary")
async def search_dictionary():
   result = await search_service.return_dictionary()
   if result is not None:
      return JSONResponse([clean(doc) for doc in result])
   return JSONResponse({"error": "not found"}, status_code=404)