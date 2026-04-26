from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
EXTRACTOR_DIR = BACKEND_ROOT / "extractor"
OUTPUT_DIR = EXTRACTOR_DIR / "Output"
INPUT_DIR = EXTRACTOR_DIR / "Input"
JSON_DATA_PATH = INPUT_DIR / "main"

USE_DB = True
COLLECTION_JOB = "jobs_id"
COLLECTION_SENT = "sentences"
COLLECTION_RESULTS = "results"