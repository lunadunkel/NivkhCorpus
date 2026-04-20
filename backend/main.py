from fastapi import FastAPI

from contextlib import asynccontextmanager
from backend.api.api_router import api_router
from backend.core.config import COLLECTION_JOB, FRONTEND_DIR, USE_DB
from fastapi.staticfiles import StaticFiles

from backend.mongodb.repositories.database import get_collection

@asynccontextmanager
async def lifespan(app: FastAPI):

    if USE_DB:
        collection = get_collection(COLLECTION_JOB)

        await collection.create_index(
            "created_at",
            expireAfterSeconds=3600
        )

    yield


app = FastAPI()
app.include_router(api_router)

# Middleware, чтобы запретить кеширование (пока разработка)
@app.middleware("http")
async def no_cache(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response

# Подключение статики
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")