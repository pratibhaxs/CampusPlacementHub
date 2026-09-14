from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.question import Question
from app.models.round import RecruitmentRound
from app.models.experience import Experience

router = APIRouter(prefix="/questions", tags=["questions"])


def _approved_question_query(db: Session):
    return (
        db.query(Question, RecruitmentRound, Experience)
        .join(RecruitmentRound, Question.round_id == RecruitmentRound.id)
        .join(Experience, RecruitmentRound.experience_id == Experience.id)
        .filter(Experience.status == "approved")
    )


@router.get("")
def list_questions(
    category: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    company_id: Optional[int] = None,
    college_id: Optional[int] = None,
    role_id: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Public. Browsable question repository. Each result includes a
    `report_count` — how many times a question with the same topic
    (case-insensitive) has been reported across approved experiences.
    """
    query = _approved_question_query(db)

    if category and category.strip():
        query = query.filter(Question.category == category.strip())
    if topic and topic.strip():
        query = query.filter(Question.topic.ilike(f"%{topic.strip()}%"))
    if difficulty and difficulty.strip():
        query = query.filter(Question.difficulty == difficulty.strip())
    if company_id:
        query = query.filter(Experience.company_id == company_id)
    if college_id:
        query = query.filter(Experience.college_id == college_id)
    if role_id:
        query = query.filter(Experience.role_id == role_id)
    if year:
        query = query.filter(Experience.placement_year == year)

    rows = query.order_by(Experience.created_at.desc()).limit(200).all()

    topic_counts = dict(
        db.query(func.lower(Question.topic), func.count(Question.id))
        .join(RecruitmentRound, Question.round_id == RecruitmentRound.id)
        .join(Experience, RecruitmentRound.experience_id == Experience.id)
        .filter(Experience.status == "approved", Question.topic.isnot(None), Question.topic != "")
        .group_by(func.lower(Question.topic))
        .all()
    )

    result = []
    for question, round_obj, experience in rows:
        data = question.to_dict()
        data["report_count"] = topic_counts.get((question.topic or "").lower(), 1)
        data["round_type"] = round_obj.round_type
        data["company_id"] = experience.company_id
        data["company_name"] = experience.company.name if experience.company else None
        data["college_name"] = experience.college.name if experience.college else None
        data["role_title"] = experience.role.title if experience.role else None
        data["placement_year"] = experience.placement_year
        data["experience_id"] = experience.id
        result.append(data)

    return result


@router.get("/frequent")
def frequent_topics(limit: int = 10, company_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Public. Top-N topics by report count via plain GROUP BY/COUNT — no ML.
    Optional ?company_id= to scope to one company (used on the company page).
    """
    limit = max(1, min(limit, 50))  # clamp — don't let a huge/negative limit hit the DB

    query = (
        db.query(func.min(Question.topic).label("topic"), func.count(Question.id).label("count"))
        .join(RecruitmentRound, Question.round_id == RecruitmentRound.id)
        .join(Experience, RecruitmentRound.experience_id == Experience.id)
        .filter(Experience.status == "approved", Question.topic.isnot(None), Question.topic != "")
    )
    if company_id:
        query = query.filter(Experience.company_id == company_id)

    rows = query.group_by(func.lower(Question.topic)).order_by(func.count(Question.id).desc()).limit(limit).all()

    return [{"topic": topic, "count": count} for topic, count in rows]
