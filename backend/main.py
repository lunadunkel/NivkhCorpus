from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from fastapi.responses import FileResponse

from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.api.router import router as api_router
from backend.api.seo import router as seo_router
from backend.core.templates import TEMPLATES
from backend.core.config import COLLECTION_JOB, COLLECTION_RESULTS, COLLECTION_SENT, FRONTEND_DIR, SITE, TEMPLATES_DIR

# from backend.app.api.api_router import api_router
# from backend.app.api.seo import router as seo_router
# from backend.app.core.config import COLLECTION_JOB, COLLECTION_RESULTS, COLLECTION_SENT, FRONTEND_DIR

# from backend.app.db.repositories.database import get_collection, ping_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # collection = get_collection(COLLECTION_JOB)

    # await collection.create_index(
    #     "created_at",
    #     expireAfterSeconds=3600
    # )
    # await collection.create_index(
    #     "query_hash",
    #     unique=True
    # )

    # main_fields = ["tokens.token", "tokens.lemma", "tokens.tagsets.Number[subj]",
    #                 "tokens.tagsets.Case", "tokens.tagsets.Person[subj]", "tokens.tagsets.Tense", "tokens.tagsets.POS"]
    # sentences = get_collection(COLLECTION_SENT)

    # for field in main_fields:
    #     await sentences.create_index(field)

    # results = get_collection(COLLECTION_RESULTS)
    # await results.create_index('job_id')
    # await results.create_index(
    #     "created_at",
    #     expireAfterSeconds=3600
    # )

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