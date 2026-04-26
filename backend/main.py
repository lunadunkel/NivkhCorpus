from fastapi import FastAPI

from contextlib import asynccontextmanager
from backend.api.api_router import api_router
from backend.core.config import COLLECTION_JOB, COLLECTION_RESULTS, COLLECTION_SENT, FRONTEND_DIR, USE_DB
from fastapi.staticfiles import StaticFiles

from backend.mongodb.repositories.database import get_collection, ping_db

@asynccontextmanager
async def lifespan(app: FastAPI):

    if USE_DB:
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


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

# Middleware, чтобы запретить кеширование (пока разработка)
@app.middleware("http")
async def no_cache(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response

# Подключение статики
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")


@app.get("/ping")
async def ping():
    await ping_db()
    return {"status": "ok"}