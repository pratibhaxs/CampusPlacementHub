from typing import Optional
from pydantic import BaseModel, Field


class CollegeIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
