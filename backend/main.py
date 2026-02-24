from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.api import search
from backend.core.config import FRONTEND_DIR, OUTPUT_DIR
from backend.services.prepare_for_html import CSVConverter

app = FastAPI()

# Подключение маршрутов
app.include_router(search.router)

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
    csv_path = OUTPUT_DIR / "search_result.csv"
    if not csv_path.exists():
        return JSONResponse({"error": "No output yet"}, status_code=404)
    converter = CSVConverter()
    json_data = converter.convert()
    return JSONResponse(json_data)