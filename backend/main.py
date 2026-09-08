from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from fastapi.responses import FileResponse

from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.api.router import router as api_router
from backend.api.seo import router as seo_router
from backend.core.templates import TEMPLATES
from backend.core.config import CORPORA, FRONTEND_DIR, TEMPLATES_DIR
from backend.db.indexes import ensure_indexes

@asynccontextmanager
async def lifespan(app: FastAPI):
    for corpus_id in CORPORA:
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
async def main_page():
    return FileResponse(TEMPLATES_DIR / "index.html")
    # return TEMPLATES.TemplateResponse()

# @app.get("/ping")
# async def ping():
#     await ping_db()
#     return {"status": "ok"}