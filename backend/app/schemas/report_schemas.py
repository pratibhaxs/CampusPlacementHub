from typing import Literal
from pydantic import BaseModel


class ReportIn(BaseModel):
    experience_id: int
    reason: Literal["fake", "inappropriate", "spam", "incorrect"]


class ReportStatusIn(BaseModel):
    status: Literal["open", "reviewed"] = "reviewed"
