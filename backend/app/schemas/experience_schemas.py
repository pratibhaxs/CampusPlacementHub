from typing import Optional, Literal, List
from pydantic import BaseModel, Field

YEAR_MIN, YEAR_MAX = 2000, 2100


class QuestionIn(BaseModel):
    question_text: str = Field(min_length=2, max_length=2000)
    category: Optional[str] = Field(default=None, max_length=50)
    topic: Optional[str] = Field(default=None, max_length=100)
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None


class RoundIn(BaseModel):
    round_number: int = Field(ge=1, le=20)
    round_type: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=3000)
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    questions: List[QuestionIn] = Field(default_factory=list)


class ExperienceIn(BaseModel):
    # --- Basic Information ---
    company_id: int
    role_id: int
    college_id: int
    branch: Optional[str] = Field(default=None, max_length=100)
    graduation_year: Optional[int] = Field(default=None, ge=YEAR_MIN, le=YEAR_MAX)
    placement_year: int = Field(ge=YEAR_MIN, le=YEAR_MAX)
    package: Optional[str] = Field(default=None, max_length=50)

    # --- Recruitment Process ---
    rounds: List[RoundIn] = Field(default_factory=list)

    # --- Final Experience ---
    overall_experience: Optional[str] = Field(default=None, max_length=5000)
    preparation_tips: Optional[str] = Field(default=None, max_length=3000)
    additional_advice: Optional[str] = Field(default=None, max_length=3000)
    selected: bool = False


class StatusUpdateIn(BaseModel):
    status: Literal["pending", "approved", "rejected"]
