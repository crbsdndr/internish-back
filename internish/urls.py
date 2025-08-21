from fastapi import APIRouter
from user_app import urls

router = APIRouter()

router.include_router(urls.router_private)
router.include_router(urls.router_public)

@router.get("/")
def read_root():
    return {"message": "Auth Service API"}