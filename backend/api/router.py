from fastapi import APIRouter
from backend.api import pages, search

router = APIRouter()

router.include_router(search.router)
router.include_router(pages.router)