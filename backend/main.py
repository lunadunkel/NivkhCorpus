from fastapi import FastAPI

from backend.api.api_router import api_router
from backend.core.config import FRONTEND_DIR
from fastapi.staticfiles import StaticFiles


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