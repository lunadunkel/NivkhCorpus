from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from api import search
import json

app = FastAPI()

# Подключение маршрутов
app.include_router(search.router)

# Путь к фронтенду
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# Middleware, чтобы запретить кеширование (пока разработка)
@app.middleware("http")
async def no_cache(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response

# Подключение статики
app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")

# index.html
@app.get("/", response_class=FileResponse)
def root():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/search_output.html", response_class=FileResponse)
def search_page():
    return FileResponse(FRONTEND_DIR / "search_output.html")

@app.get("/get_output", response_class=FileResponse)
def get_output_data():
    with open('output.json') as file:
        content = json.load(file)
    return JSONResponse(content)