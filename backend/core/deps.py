from fastapi import HTTPException
from backend.core.config import ACTIVE_CORPORA


async def valid_corpus(lang: str) -> str:
    if lang not in ACTIVE_CORPORA:
        raise HTTPException(status_code=404, detail=f"Unknown corpus: {lang}")
    return lang