from fastapi import APIRouter

from backend.api import dictionary, search, frontend

api_router = APIRouter()

api_router.include_router(search.router, tags=["Search"])
api_router.include_router(frontend.router, tags=["Frontend"])
api_router.include_router(dictionary.router, tags=["Dictionary"])