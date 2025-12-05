import os
import sys
import subprocess
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .jsontoyaml import JsonToYaml
from .prepare_for_html import CSVConverter


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
    # print("Пришёл запрос:", query)
    JsonToYaml(query)
    current_dir = os.path.dirname(__file__)
    extractor_dir = os.path.abspath(os.path.join(current_dir, "..", "extractor"))
    subprocess.run([
        sys.executable,
        "EX_tractor_1.4.py",
        "--rules", "24",
        "--dir_in", "Input/main",
        "--output_txt", "Output/search_result.txt",
        "--verbosity", "1",
        "--output_csv", "Output/search_result.csv",
        "--csv_verbosity", "1"], cwd=extractor_dir)
    CSVConverter('extractor/Output/search_result.csv')
    return JSONResponse({"status": "ok", "message": f"Вы ввели: {query}"})