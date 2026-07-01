from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse
from backend.core.config import FRONTEND_DIR
from backend.services import search_service
from backend.mongodb.repositories.utils import clean

router = APIRouter(prefix="/dictionary", tags=["Dictionary"])

# dictionary.html
@router.get("")
def dictionary():
    return FileResponse(FRONTEND_DIR / "dictionary.html")


@router.get("/word")
async def word_page():
    return FileResponse(FRONTEND_DIR / "word.html")

@router.get("/list/{letter}")
async def list_by_letter(letter: str):
    result = await search_service.return_letter_list(letter)
    cleaned_results = [clean(doc) for doc in result]
    return cleaned_results

@router.get("/{letter}")
async def letter_page(letter: str):
    return FileResponse(FRONTEND_DIR / "letter.html")