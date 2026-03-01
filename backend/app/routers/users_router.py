from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Role
from app.auth import require_admin, get_password_hash
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return db.query(User).all()


@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже есть")
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
        role=data.role or Role.operator.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )
