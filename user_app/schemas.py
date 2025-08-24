from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Optional
from pydantic import EmailStr

class LoginUser(BaseModel):
    email_: EmailStr
    password_: str

class StudentExtra(BaseModel):
    id_: Optional[int] = None
    student_number_: Annotated[str, StringConstraints(min_length=3)]
    national_sn_: Annotated[str, StringConstraints(min_length=3)]
    major_: str
    batch_: Annotated[str, StringConstraints(min_length=2)]
    notes_: str | None = None
    photo_: str | None = None

class SupervisorExtra(BaseModel):
    id_: Optional[int] = None
    supervisor_number_: Annotated[str, StringConstraints(min_length=3)]
    department_: str
    notes_: str | None = None
    photo_: str | None = None

class UserCreate(BaseModel):
    id_: Optional[int] = None
    full_name_: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    email_: EmailStr
    phone_: Annotated[str, StringConstraints(strip_whitespace=True, min_length=4)]
    password_: str
    role_: Annotated[
        str,
        StringConstraints(strip_whitespace=True, pattern=r"^(student|supervisor|developer)$")
    ]
    student_: Optional[StudentExtra] = None
    supervisor_: Optional[SupervisorExtra] = None

class UserUpdate(UserCreate):
    password_: str | None = None