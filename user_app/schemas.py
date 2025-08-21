from pydantic import BaseModel, Field
from enum import Enum

class LoginUser(BaseModel):
    email_: str = Field(...)
    password_: str = Field(..., alias="password_")

class User(LoginUser):
    class Role(str, Enum):
        student = "student"
        supervisor = "supervisor"
        developer = "developer"

    full_name_: str = Field(...)
    phone_: str = Field(...)
    role_: Role = Field(...)

class RefreshRequest(BaseModel):
    refresh_token: str