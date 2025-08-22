from fastapi import APIRouter
from user_app.urls import user_router_public, user_router_private
# from student_app.urls import student_router_public, student_router_private

router = APIRouter()

router.include_router(user_router_private)
router.include_router(user_router_public)
# router.include_router(student_router_private)
# router.include_router(student_router_public)

@router.get("/")
def read_root():
    return {"message": "Auth Service API"}