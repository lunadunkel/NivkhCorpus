from fastapi import APIRouter, Depends

from backend.api import dictionary, search, frontend
from backend.core.deps import valid_corpus

api_router = APIRouter()

corpus_guard = [Depends(valid_corpus)]

api_router.include_router(search.router, tags=["Search"], dependencies=corpus_guard)
api_router.include_router(frontend.router, tags=["Frontend"], dependencies=corpus_guard)
api_router.include_router(dictionary.router, tags=["Dictionary"], dependencies=corpus_guard)