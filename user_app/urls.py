from fastapi import APIRouter, HTTPException, status, Depends
from user_app import views, serializers, schemas
from datetime import datetime, timedelta, timezone

from internish.settings import config_jwt
from internish.schemas import TokenResponse, RefreshRequest
from internish.security import make_access_token, make_refresh_token, decode_token, require_auth

router_public = APIRouter(prefix="/users", tags=["users"])
router_private = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_auth)],
)

@router_private.get("/")
def read_root():
    return views.user_interact.list()

@router_private.get("/{id}")
def read_item(id: int):
    return views.user_interact.index(id)

@router_public.post("/signup")
def create_item(item: schemas.User):
    item.password_ = serializers.user_serializer.password_hash(item.password_)
    return views.user_interact.create(item)

@router_public.post("/login")
def verify_item(item: schemas.LoginUser):
    user = views.user_interact.index(email=item.email_)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"status": False, "message": "User not found"})

    if not serializers.user_serializer.verify_password(item.password_, user["password_hash_"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"status": False, "message": "Invalid password"})

    access = make_access_token(sub=user["email_"], extra={"role": user["role_"]})
    refresh = make_refresh_token(sub=user["email_"])

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=config_jwt.REFRESH_EXPIRE_MIN)
    views.user_interact.save_refresh(user["email_"], refresh, expires_at)

    return TokenResponse(access_token=access, refresh_token=refresh)

@router_public.post("/refresh", response_model=TokenResponse)
def refresh_token(item: RefreshRequest):
    try:
        payload = decode_token(item.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail={"status": False, "message": "Token is not a refresh token"})
        sub = payload.get("sub")

    except Exception:
        raise HTTPException(status_code=401, detail={"status": False, "message": "Refresh token is invalid or expired"})

    rt = views.user_interact.get_refresh(item.refresh_token)
    if not rt:
        raise HTTPException(status_code=401, detail={"status": False, "message": "Refresh token is not registered"})

    if rt["revoked_"]:
        raise HTTPException(status_code=401, detail={"status": False, "message": "Refresh token is revoked"})

    if rt["expires_at_"] <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail={"status": False, "message": "Refresh token is expired"})

    new_access = make_access_token(sub=sub, extra={"role": "student"})

    return TokenResponse(access_token=new_access, refresh_token=item.refresh_token)


@router_private.post("/logout")
def logout(item: schemas.LogoutRequest):
    payload = decode_token(item.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Bukan refresh token")

    try:
        views.user_interact.revoke_refresh(item.refresh_token)
    except Exception:
        pass

    return {"message": "Logged out (refresh token revoked)"}


@router_private.post("/logout-all")
def logout_all(item: schemas.LogoutAllRequest):
    payload = decode_token(item.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Bukan refresh token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token tidak valid")

    views.user_interact.revoke_all_refresh_by_email(email)
    return {"message": "All sessions revoked"}