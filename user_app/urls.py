from user_app.utils import user_utils
from user_app.views import user_interact
from user_app.helpers import user_helper
from user_app.schemas import LoginUser, UserCreate

from internish.settings import config_jwt
from internish.schemas import TokenResponse, RefreshRequest
from internish.security import decode_token, require_auth

from fastapi import APIRouter, HTTPException, status, Depends

user_router_public = APIRouter(prefix="/users", tags=["users"])
user_router_private = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_auth)],
)

@user_router_private.get("/")
def read_root():
    return user_interact.list()

@user_router_public.post("/user/signup")
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

@user_router_public.post("/user/login")
def verify_item(item: LoginUser):
    try:
        result = user_helper.login_user(item.email_, item.password_)
        return TokenResponse(**result)
    
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": str(ve)}
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status": False, "message": f"Login error: {str(e)}"})

@user_router_public.post("/user/refresh-access-token", response_model=TokenResponse)
def refresh_token(item: RefreshRequest):
    try:
        result = user_helper.refresh_access_token(item.refresh_token_)
        return TokenResponse(**result)
    except ValueError as ve:
        raise HTTPException(
            status_code=401,
            detail={"status": False, "message": str(ve)}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={"status": False, "message": str(e)}
        )

@user_router_private.post("/user/logout")
def logout(item: RefreshRequest):
    payload = decode_token(item.refresh_token_)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail={"status": False, "message": "Not a refresh token"}
        )

    try:
        user_helper.revoke_refresh(item.refresh_token_)

    except Exception:
        pass

    return {"message": "Logged out (refresh token revoked)"}

@user_router_private.post("/user/logout-all")
def logout_all(item: RefreshRequest):
    try:
        return user_helper.logout_all_sessions(item.refresh_token_)
    except ValueError as ve:
        raise HTTPException(
            status_code=401,
            detail={"status": False, "message": str(ve)}
        )

@user_router_private.post("/user/protected")
def protected(item: RefreshRequest):
    payload = decode_token(item.refresh_token_)
    return payload

@user_router_private.get("/user/{id}")
def read_item(id: int):
    return user_interact.index(id)