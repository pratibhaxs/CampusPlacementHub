from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.experience import Experience
from app.models.question import Question
from app.models.round import RecruitmentRound
from app.security import role_required

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/statistics")
def platform_statistics(
    db: Session = Depends(get_db),
    _admin: User = Depends(role_required("admin")),
):
    """Admin-only. Platform-wide counts via plain SQL aggregation."""
    total_students = db.query(User).filter_by(role="student").count()
    total_alumni = db.query(User).filter_by(role="alumni").count()
    total_companies = db.query(Company).count()
    total_experiences = db.query(Experience).filter_by(status="approved").count()
    pending_experiences = db.query(Experience).filter_by(status="pending").count()

    most_discussed = (
        db.query(Company.name, func.count(Experience.id).label("count"))
        .join(Experience, Experience.company_id == Company.id)
        .filter(Experience.status == "approved")
        .group_by(Company.id)
        .order_by(func.count(Experience.id).desc())
        .limit(5)
        .all()
    )

    most_frequent_topics = (
        db.query(func.min(Question.topic).label("topic"), func.count(Question.id).label("count"))
        .join(RecruitmentRound, Question.round_id == RecruitmentRound.id)
        .join(Experience, RecruitmentRound.experience_id == Experience.id)
        .filter(Experience.status == "approved", Question.topic.isnot(None), Question.topic != "")
        .group_by(func.lower(Question.topic))
        .order_by(func.count(Question.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_students": total_students,
        "total_alumni": total_alumni,
        "total_companies": total_companies,
        "total_experiences": total_experiences,
        "pending_experiences": pending_experiences,
        "most_discussed_companies": [{"company": name, "count": count} for name, count in most_discussed],
        "most_frequent_topics": [{"topic": topic, "count": count} for topic, count in most_frequent_topics],
    }
