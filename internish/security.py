from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends

from jose import jwt, JWTError
from internish.settings import config_jwt

JWT_SECRET = config_jwt.JWT_SECRET
JWT_ALG = config_jwt.JWT_ALG
ACCESS_EXPIRE_MIN = config_jwt.ACCESS_EXPIRE_MIN
REFRESH_EXPIRE_MIN = config_jwt.REFRESH_EXPIRE_MIN

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def _encode(claims: Dict[str, Any], minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    claims = {**claims, "exp": expire}
    return jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALG)

def make_access_token(sub: str, extra: Dict[str, Any] = None) -> str:
    payload = {"sub": sub, "type": "access"}
    if extra:
        payload.update(extra)
    return _encode(payload, ACCESS_EXPIRE_MIN)

def make_refresh_token(sub: str) -> str:
    payload = {"sub": sub, "type": "refresh"}
    return _encode(payload, REFRESH_EXPIRE_MIN)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "Token is not valid or expired"},
        )

def require_auth(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"status": False, "message": "Wrong token type"})

    sub = payload.get("sub")

    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"status": False, "message": "Invalid token payload"})

    return {"email": sub, "role": payload.get("role")}

def get_metadata_access_token(access_token: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token tidak ada")
    
    token = auth_header.split(" ")[1]  # ambil bagian setelah "Bearer"
    return token