from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.core.config import SITE
from backend.core.deps import CorpusDep
from backend.core.it_text import format_grammar
from backend.core.templates import TEMPLATES
from backend.core import search_service
from backend.db.compile.process_query import QueryBuilder
from backend.db.repositories.utils import clean

router = APIRouter(prefix="/{corpus_name}/search", tags=["search"])

@router.post("/")
async def search(request: Request, corpus: CorpusDep):
    query = await request.json()
    return await search_service.search(corpus, query=query)

@router.post("/doc_id={doc_id}")
async def search_glossing(request: Request, doc_id: str, corpus: CorpusDep):
   result = await search_service.add_glossing(corpus.id, doc_id)
   if result is not None:
      return {"segmentation": result.get('segmented_text', ''), "glossing": result.get('glossed_text', '')}
   return JSONResponse({"error": "not found"}, status_code=404)

@router.get("/dictionary")
async def search_dictionary(request: Request, corpus: CorpusDep):
   result = await search_service.return_dictionary(corpus.id)
   if result is not None:
      return JSONResponse([clean(doc) for doc in result])
   return JSONResponse({"error": "not found"}, status_code=404)

@router.post("/preview")
async def preview(request: Request, corpus: CorpusDep):
   form = await request.json()
   query = QueryBuilder(corpus, [form]).queries[0]
   return {"text": format_grammar(query.conditions)}

@router.get("/form")
async def search_form(job_id: str, corpus: CorpusDep):
   form = await search_service.get_form(corpus, job_id)
   if form is None:
      return JSONResponse({"error": "not found"}, status_code=404)
   return form

@router.post("/update_filter")
async def update_texts(corpus: CorpusDep, job_id: str, condition: dict, sort: str = "default", offset: int = 0):
   return await search_service.get_meta(corpus, job_id, condition, sort, offset)

@router.get("/copy={example_id}")
async def copy_example(corpus: CorpusDep, example_id: str):
   return await search_service.copy_example(corpus, example_id)