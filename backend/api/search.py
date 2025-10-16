from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/")
async def search(request: Request):
    """
    Здесь надо понимать, что реквест приходит json список
    Его нужно обработать отдельно, наверно, классом обработки в ямл
    то есть типа отдельно на беке создать класс с функциями и сюда вернуть уже готовый ямл
    """
    data = await request.json()
    query = data
    print("Пришёл запрос:", query)
    return JSONResponse({"status": "ok", "message": f"Вы ввели: {query}"})