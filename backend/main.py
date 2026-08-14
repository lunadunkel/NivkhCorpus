from fastapi import FastAPI, Request

from contextlib import asynccontextmanager

from fastapi.responses import FileResponse, JSONResponse
from backend.api.api_router import api_router
from backend.api.seo import router as seo_router
from backend.core.config import COLLECTION_JOB, COLLECTION_RESULTS, COLLECTION_SENT, FRONTEND_DIR
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.mongodb.repositories.database import get_collection, ping_db

@asynccontextmanager
async def lifespan(app: FastAPI):

    collection = get_collection(COLLECTION_JOB)

    await collection.create_index(
        "created_at",
        expireAfterSeconds=3600
    )
    await collection.create_index(
        "query_hash",
        unique=True
    )

    main_fields = ["tokens.token", "tokens.lemma", "tokens.tagsets.Number[subj]",
                    "tokens.tagsets.Case", "tokens.tagsets.Person[subj]", "tokens.tagsets.Tense", "tokens.tagsets.POS"]
    sentences = get_collection(COLLECTION_SENT)

    for field in main_fields:
        await sentences.create_index(field)

    results = get_collection(COLLECTION_RESULTS)
    await results.create_index('job_id')
    await results.create_index(
        "created_at",
        expireAfterSeconds=3600
    )

    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(seo_router)
app.include_router(api_router)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    wants_html = "text/html" in request.headers.get("accept", "")
    if exc.status_code == 404 and wants_html:
        return FileResponse(FRONTEND_DIR / "404.html", status_code=404)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

@app.get("/")
async def main_page():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/ping")
async def ping():
    await ping_db()
    return {"status": "ok"}