from typing import Annotated, Optional

from pydantic import BaseModel, StringConstraints, Field


class Application(BaseModel):
    id_: Optional[int] = None
    student_id_: Optional[int] = None
    institution_id_: Annotated[int, Field(gt=0)]
    period_: Annotated[str, StringConstraints(min_length=1)]
    status_: Annotated[
        str,
        StringConstraints(pattern=r"^(pending|testing|accepted|rejected|under_review)$")
    ] | None = None
    notes_: str | None = None
    applied_at_: Optional[str] = None
