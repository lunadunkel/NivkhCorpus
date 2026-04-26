from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from backend.core.config import COLLECTION_RESULTS, FRONTEND_DIR, OUTPUT_DIR, USE_DB
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
async def get_output_data(job_id: str, offset: int = 0, limit: int = 20):
    if not USE_DB:
        csv_path = OUTPUT_DIR / "search_result.csv"
        if not csv_path.exists():
            return JSONResponse({"error": "No output yet"}, status_code=404)
        converter = CSVConverter()
        json_data = converter.convert()
        return JSONResponse(json_data)
    else:
        collection = get_collection(COLLECTION_RESULTS)
        total = await collection.count_documents({"job_id": job_id})
        if total == 0:
            return JSONResponse({"error": "not found"}, status_code=404)

        cursor = collection.find({"job_id": job_id}).skip(offset).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        if not docs:
            return {"error": "not found"}
        cleaned_results = [clean(doc['result']) for doc in docs]
        return JSONResponse({"results": cleaned_results, "length": total})