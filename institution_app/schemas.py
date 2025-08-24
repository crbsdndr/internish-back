from pydantic import BaseModel, StringConstraints, Field
from typing import Annotated, Optional
from pydantic import EmailStr

class InstitutionQuotas(BaseModel):
    # id_ : Optional[int] = None
    institution_id_: Annotated[str, StringConstraints(min_length=1)]
    period_: Annotated[str, StringConstraints(min_length=1)]
    quota_: Annotated[int, Field(gt=0)]

class InstitutionContacts(BaseModel):
    # id_ : Optional[int] = None
    institution_id_: Annotated[str, StringConstraints(min_length=1)]
    phone_: Annotated[str, StringConstraints(min_length=4, max_length=20)] | None = None
    email_: EmailStr | None = None
    position_: Annotated[str, StringConstraints(min_length=2)] | None = None
    is_primary_: bool | None = None

class Institution(BaseModel):
    # id_ : Optional[int] = None
    name_: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    address_: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    photo_: str | None = None
    notes_: str | None = None

    institution_contacts_: Optional[InstitutionContacts] = None
    institution_quotas_: Optional[InstitutionQuotas] = None
