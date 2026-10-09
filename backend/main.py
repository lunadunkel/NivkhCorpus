from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from fastapi.responses import FileResponse

from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.api.router import router as api_router
from backend.api.seo import router as seo_router
from backend.core import fetch_stats
from backend.core.templates import TEMPLATES
from backend.core.config import CORPORA, FRONTEND_DIR, TEMPLATES_DIR
from backend.db.database import get_collection
from backend.db.indexes import ensure_indexes

@asynccontextmanager
async def lifespan(app: FastAPI):
    for corpus_id, cfg in CORPORA.items():
        collection = get_collection(corpus_id, 'sentences')
        genres = await collection.distinct("metadata.genre")
        genres = {genre: f'g{number}' for number, genre in enumerate(sorted(genres))}
        dialects = await collection.distinct("metadata.dialect")
        dialects = {dialect: f'd{number}' for number, dialect in enumerate(sorted(dialects))}
        dates = await collection.distinct("metadata.date")

        meta = {'genre': genres, 'dialect': dialects, "date": len(dates) > 1}
        CORPORA[corpus_id] = cfg.model_copy(update={"meta": meta})
        await ensure_indexes(corpus_id)
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(seo_router)
app.include_router(api_router)

@app.middleware("http")
async def disable_static_cache(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    wants_html = "text/html" in request.headers.get("accept", "")
    if exc.status_code == 404 and wants_html:
        return TEMPLATES.TemplateResponse(request, "404.html", status_code=404)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.get("/")
async def main_page(request: Request):
    statistics = await fetch_stats.fetch_per_corpus()
    return TEMPLATES.TemplateResponse(request, "index.html", {"stats": statistics})

# @app.get("/ping")
# async def ping():
#     await ping_db()
#     return {"status": "ok"}