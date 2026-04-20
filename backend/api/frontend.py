from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from backend.core.config import COLLECTION_JOB, FRONTEND_DIR, OUTPUT_DIR, USE_DB
from backend.mongodb.repositories.utils import clean
from backend.services.prepare_for_html import CSVConverter
from backend.mongodb.repositories.database import get_collection


router = APIRouter()

# index.html
@router.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html")

# search_output.html
@router.get("/search_output.html")
def search_page():
    return FileResponse(FRONTEND_DIR / "search_output.html")

@router.get("/get_output")
async def get_output_data(job_id: str):
    if not USE_DB:
        csv_path = OUTPUT_DIR / "search_result.csv"
        if not csv_path.exists():
            return JSONResponse({"error": "No output yet"}, status_code=404)
        converter = CSVConverter()
        json_data = converter.convert()
        return JSONResponse(json_data)
    else:
        collection = get_collection(COLLECTION_JOB)
        doc = await collection.find_one({"_id": job_id})
        if not doc:
            return {"error": "not found"}

        return clean(doc["result"])