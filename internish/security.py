from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from typing import Dict, Any
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

JWT_SECRET = "UBAH_INI_RANDOM" 
JWT_ALG = "HS256"
ACCESS_EXPIRE_MIN = 30
REFRESH_EXPIRE_MIN = 60 * 24 * 7  

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
            detail="Token tidak valid atau sudah kedaluwarsa",
        )
    

def require_auth(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type")
    sub = payload.get("sub")

    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    return {"email": sub, "role": payload.get("role")}