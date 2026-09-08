from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.core.config import SITE
from backend.core.deps import CorpusDep
from backend.core.templates import TEMPLATES
from backend.core import search_service
from backend.db.repositories.utils import clean

router = APIRouter(prefix="/{corpus_name}/search", tags=["search"])

@router.post("/")
async def search(request: Request, corpus: CorpusDep):
    query = await request.json()
    print(query)
    return await search_service.search(lang=corpus.id, query=query)

@router.post("/doc_id={doc_id}")
async def search_glossing(request: Request, doc_id: str, corpus: CorpusDep):
   result = await search_service.add_glossing(corpus.id, doc_id)
   if result is not None:
      return {"segmentation": result['segmented_text'], "glossing": result['glossed_text']}
   return JSONResponse({"error": "not found"}, status_code=404)

@router.get("/dictionary")
async def search_dictionary(request: Request, corpus: CorpusDep):
   result = await search_service.return_dictionary(corpus.id)
   if result is not None:
      return JSONResponse([clean(doc) for doc in result])
   return JSONResponse({"error": "not found"}, status_code=404)