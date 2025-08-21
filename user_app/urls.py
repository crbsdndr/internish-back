from user_app.utils import user_utils
from user_app.views import user_interact
from user_app.schemas import User, LoginUser, RefreshRequest

from internish.settings import config_jwt
from internish.schemas import TokenResponse, RefreshRequest
from internish.security import make_access_token, make_refresh_token, decode_token, require_auth

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta, timezone


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
def create_item(item: User):
    item.password_ = user_utils.password_hash(item.password_)
    return user_interact.create(item)

@user_router_public.post("/user/login")
def verify_item(item: LoginUser):
    user = user_interact.index(email=item.email_)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"status": False, "message": "User not found"})

    if not user_utils.verify_password(item.password_, user["password_hash_"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"status": False, "message": "Invalid password"})

    access = make_access_token(sub=user["email_"], extra={"role": user["role_"]})
    refresh = make_refresh_token(sub=user["email_"])

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=config_jwt.REFRESH_EXPIRE_MIN)
    user_interact.save_refresh(user["email_"], refresh, expires_at)

    return TokenResponse(access_token=access, refresh_token=refresh)

@user_router_private.post("/user/refresh", response_model=TokenResponse)
def refresh_token(item: RefreshRequest):
    try:
        payload = decode_token(item.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail={"status": False, "message": "Not a refresh token"})
        sub = payload.get("sub")

    except Exception:
        raise HTTPException(status_code=401, detail={"status": False, "message": "Refresh token is invalid or expired"})

    rt = user_interact.get_refresh(item.refresh_token)
    if not rt:
        raise HTTPException(status_code=401, detail={"status": False, "message": "Refresh token is not registered"})

    if rt["revoked_"]:
        raise HTTPException(status_code=401, detail={"status": False, "message": "Refresh token is revoked"})

    if rt["expires_at_"] <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail={"status": False, "message": "Refresh token is expired"})

    new_access = make_access_token(sub=sub, extra={"role": "student"})

    return TokenResponse(access_token=new_access, refresh_token=item.refresh_token)


@user_router_private.post("/user/logout")
def logout(item: RefreshRequest):
    payload = decode_token(item.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail={"status": False, "message": "Not a refresh token"})

    try:
        user_interact.revoke_refresh(item.refresh_token)
    except Exception:
        pass

    return {"message": "Logged out (refresh token revoked)"}

@user_router_private.post("/user/logout-all")
def logout_all(item: RefreshRequest):
    payload = decode_token(item.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail={"status": False, "message": "Not a refresh token"})

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail={"status": False, "message": "Token is not valid"})

    user_interact.revoke_all_refresh_by_email(email)
    return {"message": "All sessions revoked"}

@user_router_private.post("/user/protected")
def protected(item: RefreshRequest):
    print("Masuk woi")
    payload = decode_token(item.refresh_token)
    return payload

@user_router_private.get("/user/{id}")
def read_item(id: int):
    return user_interact.index(id)