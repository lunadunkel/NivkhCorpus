from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from backend.core.config import COLLECTION_JOB, COLLECTION_RESULTS, FRONTEND_DIR
from backend.mongodb.repositories.utils import clean
from backend.core import search_service
from backend.mongodb.repositories.database import get_collection


router = APIRouter(prefix="/{lang}")

# search.html
@router.get("/")
async def language_page(lang: str):
    return FileResponse(FRONTEND_DIR / "search.html")

# search_output.html
@router.get("/search_output")
def search_page():
    return FileResponse(FRONTEND_DIR / "search_output.html")

# about.html
@router.get("/about")
def about():
    return FileResponse(FRONTEND_DIR / "about.html")

@router.get("/get_output")
async def get_output_data(job_id: str, offset: int = 0, limit: int = 20):
    job_exists = await get_collection(COLLECTION_JOB).find_one({"_id": job_id})
    if not job_exists:
        return JSONResponse({"error": "job not found"}, status_code=404)
    
    collection = get_collection(COLLECTION_RESULTS)
    total = await collection.count_documents({"job_id": job_id})

    cursor = collection.find({"job_id": job_id}).skip(offset).limit(limit)
    docs = await cursor.to_list(length=limit)

    cleaned_results = [clean(doc['result']) for doc in docs]

    return JSONResponse({
        "results": cleaned_results,
        "length": total
    })