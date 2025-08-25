from typing import Annotated, Optional
from datetime import date

from pydantic import BaseModel, Field, StringConstraints


class Internship(BaseModel):
    id_: Optional[int] = None
    application_id_: Annotated[int, Field(gt=0)]
    supervisor_id_: Optional[int] = None
    start_date_: Optional[date] = None
    end_date_: Optional[date] = None
    status_: Annotated[
        str,
        StringConstraints(pattern=r"^(ongoing|completed|cancelled)$"),
    ] | None = None
