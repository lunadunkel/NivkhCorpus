import subprocess
import sys
import asyncio
from backend.services.jsontoyaml import JsonToYaml
from backend.core.config import EXTRACTOR_DIR

async def run_search(query):
    JsonToYaml(query)
    await asyncio.to_thread(
        lambda: subprocess.run([
            sys.executable,
            "EX_tractor_1.4.py",
            "--rules", "24",
            "--dir_in", "Input/main",
            "--output_txt", "Output/search_result.txt",
            "--verbosity", "1",
            "--output_csv", "Output/search_result.csv",
            "--csv_verbosity", "1"
        ], cwd=EXTRACTOR_DIR, check=True)
    )
    return {"status": "ok"}