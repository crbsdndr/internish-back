from fastapi import APIRouter

from auth_app.urls import router as auth_router
from user_app.urls import router as user_router
from institution_app.urls import institution_router_private

router = APIRouter()

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(institution_router_private)


@router.get("/")
def read_root():
    return {"message": "Internish Service API"}

