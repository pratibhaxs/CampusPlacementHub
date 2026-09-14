from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.college import College
from app.schemas.auth_schemas import RegisterIn, LoginIn
from app.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=payload.email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    if not db.get(College, payload.college_id):
        raise HTTPException(status_code=400, detail="Invalid college_id")

    user = User(
        name=payload.name,
        email=payload.email,
        role=payload.role,  # only "student" or "alumni" — enforced by the schema's Literal type
        college_id=payload.college_id,
        branch=payload.branch,
        graduation_year=payload.graduation_year,
    )
    user.password_hash = hash_password(payload.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role)
    return {"token": token, "user": user.to_dict()}


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated")

    token = create_access_token(user.id, user.role)
    return {"token": token, "user": user.to_dict()}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"user": current_user.to_dict()}
