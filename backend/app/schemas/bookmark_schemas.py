from typing import Literal
from pydantic import BaseModel


class BookmarkIn(BaseModel):
    target_type: Literal["experience", "question", "company"]
    target_id: int
