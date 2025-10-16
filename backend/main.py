from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# middleware, чтобы добавить no-cache
@app.middleware("http")
async def no_cache(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response

app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")

@app.get("/", response_class=FileResponse)
def root():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.post("/search")
async def search(request: Request):
    data = await request.json()
    print(data)
    # query = data.get("query")
    print("Пришёл запрос:", data)
    return JSONResponse({"status": "ok", "message": f"Вы ввели: {data}"})
