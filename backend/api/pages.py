from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.core import search_service
from backend.core.config import SITE
from backend.core.deps import CorpusDep
from backend.core.templates import TEMPLATES
from backend.db.repositories.utils import clean

router = APIRouter(prefix="/{corpus_name}", tags=["corporas"])

#search
@router.get('')
async def search_page(request: Request, corpus: CorpusDep):
    page = corpus.pages['search']
    return TEMPLATES.TemplateResponse(request, page.template, {
        "site": SITE,
        "corpus": corpus,
        "page": page,
    })

# about.html
@router.get("/about")
async def about(request: Request, corpus: CorpusDep):
    page = corpus.pages['about']
    return TEMPLATES.TemplateResponse(request, page.template, {
        "site": SITE,
        "corpus": corpus,
        "page": page,
    })

# dictionary.html
@router.get("/dictionary")
def dictionary(request: Request, corpus: CorpusDep):
    page = corpus.pages['dictionary']
    return TEMPLATES.TemplateResponse(request, page.template,
    {
        "site": SITE,
        "corpus": corpus,
        "page": page})

@router.get("/search_output")
def search_output(request: Request, corpus: CorpusDep):
    page = corpus.pages['search_output']
    return TEMPLATES.TemplateResponse(request, page.template, {"site": SITE,
            "corpus": corpus,
            "page": page})

@router.get("/get_output", include_in_schema=False)
async def get_output_data(request: Request, job_id: str, offset: int, limit: int, corpus: CorpusDep):
    result = await search_service.return_results(corpus.id, job_id, offset, limit)
    if result is None:
        return JSONResponse({"error": "job not found"}, status_code=404)
    return JSONResponse({
        "results": [clean(doc) for doc in result["results"]],
        "length": result["length"],
    })

# dictionary.html
@router.get("/dictionary/word")
async def word_page(request: Request, corpus: CorpusDep):
    page = corpus.pages['word']
    return TEMPLATES.TemplateResponse(request, page.template, {"site": SITE,
            "corpus": corpus,
            "page": page})

@router.get("/dictionary/group")
async def get_group(corpus: CorpusDep, id: str):
    result = await search_service.return_group_by_id(corpus.id, id)
    if result is None:
        return JSONResponse({"error": "not found"}, status_code=404)
    documents = [
        {
            "id": str(d["_id"]),
            "lemma": d.get("lemma"),
            "translation": d.get("translation"),
            "POS": d.get("POS"),
            "ex": d.get("ex"),     
            "tr": d.get("tr"),    
        }
        for d in result["documents"]
    ]
    return {
        "translation": result["translation"],
        "documents": documents,
    }

@router.get("/dictionary/{letter}")
async def letter_page(request: Request, letter: str, corpus: CorpusDep):
    page = corpus.pages['letter']
    return TEMPLATES.TemplateResponse(request, page.template, {"site": SITE,
            "corpus": corpus,
            "page": page})

@router.get("/dictionary/list/{letter}")
async def list_by_letter(letter: str, corpus: CorpusDep):
    result = await search_service.return_letter_list(corpus.id, letter)
    cleaned_results = [clean(doc) for doc in result]
    return cleaned_results