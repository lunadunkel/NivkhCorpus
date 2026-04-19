from fastapi import APIRouter

from backend.api import search
from backend.api import frontend

api_router = APIRouter()

api_router.include_router(search.router, tags=["Search"])
api_router.include_router(frontend.router, tags=["Frontend"])