from typing import Optional
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email_: EmailStr
    password_: str

class TokenResponse(BaseModel):
    access_token_: str
    refresh_token_: Optional[str] = None
    token_type_: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token_: str

