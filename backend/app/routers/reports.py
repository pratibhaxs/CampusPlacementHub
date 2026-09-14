from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.models.experience import Experience
from app.models.user import User
from app.schemas.report_schemas import ReportIn, ReportStatusIn
from app.security import role_required

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", status_code=201)
def create_report(
    payload: ReportIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required("student")),
):
    experience = db.get(Experience, payload.experience_id)
    if not experience or experience.status != "approved":
        raise HTTPException(status_code=404, detail="Experience not found")

    duplicate = db.query(Report).filter_by(
        user_id=current_user.id, experience_id=payload.experience_id, reason=payload.reason, status="open"
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="You've already reported this for the same reason")

    report = Report(user_id=current_user.id, experience_id=payload.experience_id, reason=payload.reason)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report.to_dict()


@router.get("")
def list_reports(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(role_required("admin")),
):
    """Admin-only. Open reports first, so the moderation queue is actionable at a glance."""
    query = db.query(Report)
    if status:
        query = query.filter_by(status=status)

    reports = query.order_by(
        (Report.status == "reviewed"),  # False (open) sorts before True (reviewed)
        Report.created_at.desc(),
    ).all()
    return [r.to_dict() for r in reports]


@router.put("/{report_id}")
def resolve_report(
    report_id: int,
    payload: ReportStatusIn,
    db: Session = Depends(get_db),
    _admin: User = Depends(role_required("admin")),
):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = payload.status
    db.commit()
    db.refresh(report)
    return report.to_dict()
