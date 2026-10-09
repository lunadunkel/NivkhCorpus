from fastapi import APIRouter
from backend.api import pages, search, export

router = APIRouter()

router.include_router(search.router)
router.include_router(pages.router)
router.include_router(export.router)