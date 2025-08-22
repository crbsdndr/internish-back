from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Optional
from enum import Enum
from pydantic import EmailStr

class LoginUser(BaseModel):
    email_: EmailStr
    password_: str

class StudentExtra(BaseModel):
    student_number: Annotated[str, StringConstraints(min_length=3)]
    national_sn:    Annotated[str, StringConstraints(min_length=3)]
    major: str
    batch: Annotated[str, StringConstraints(min_length=2)]
    notes: str | None = None
    photo: str | None = None

class SupervisorExtra(BaseModel):
    supervisor_number: Annotated[str, StringConstraints(min_length=3)]
    department: str
    notes: str | None = None
    photo: str | None = None

class UserCreate(BaseModel):
    full_name_: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    email_: EmailStr
    phone_: Annotated[str, StringConstraints(strip_whitespace=True, min_length=4)]
    password_: str
    role_: Annotated[
        str,
        StringConstraints(strip_whitespace=True, pattern=r"^(student|supervisor|developer)$")
    ]
    student: Optional[StudentExtra] = None
    supervisor: Optional[SupervisorExtra] = None


class RefreshRequest(BaseModel):
    refresh_token: str