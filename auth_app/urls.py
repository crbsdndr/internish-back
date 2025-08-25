from fastapi import APIRouter, HTTPException, status

from internish.schemas import TokenResponse, RefreshRequest
from user_app.schemas import LoginUser, UserCreate
from user_app.utils import user_utils
from user_app.views import user_interact
from auth_app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def create_user(item: UserCreate):
    try:
        item.password_ = user_utils.password_hash(item.password_)
        result = user_interact.create_user_with_role(
            user_item=item,
            student=item.student_.model_dump() if item.student_ else None,
            supervisor=item.supervisor_.model_dump() if item.supervisor_ else None,
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail={"status": False, "message": str(ve)})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"DB error: {str(e)}"})


@router.post("/login", response_model=TokenResponse)
def login(item: LoginUser):
    try:
        result = auth_service.login(item.email_, item.password_)
        return TokenResponse(**result)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": str(ve)},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"Login error: {str(e)}"})


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(item: RefreshRequest):
    try:
        result = auth_service.refresh_access_token(item.refresh_token_)
        return TokenResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=401, detail={"status": False, "message": str(ve)})
    except Exception as e:
        raise HTTPException(status_code=401, detail={"status": False, "message": str(e)})


@router.post("/logout")
def logout(item: RefreshRequest):
    try:
        auth_service.logout(item.refresh_token_)
    except Exception:
        pass
    return {"message": "Logged out (refresh token revoked)"}


@router.post("/logout-all")
def logout_all(item: RefreshRequest):
    try:
        return auth_service.logout_all(item.refresh_token_)
    except ValueError as ve:
        raise HTTPException(status_code=401, detail={"status": False, "message": str(ve)})

