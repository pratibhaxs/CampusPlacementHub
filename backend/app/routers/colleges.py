from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.college import College
from app.models.user import User
from app.schemas.college_schemas import CollegeIn
from app.security import role_required

router = APIRouter(prefix="/colleges", tags=["colleges"])


@router.get("")
def list_colleges(db: Session = Depends(get_db)):
    """Public — needed for the registration dropdown, so no auth required."""
    colleges = db.query(College).order_by(College.name).all()
    return [c.to_dict() for c in colleges]


@router.post("", status_code=201)
def create_college(
    payload: CollegeIn,
    db: Session = Depends(get_db),
    _admin: User = Depends(role_required("admin")),
):
    if db.query(College).filter_by(name=payload.name).first():
        raise HTTPException(status_code=409, detail="College already exists")

    college = College(name=payload.name, city=payload.city, state=payload.state)
    db.add(college)
    db.commit()
    db.refresh(college)
    return college.to_dict()
