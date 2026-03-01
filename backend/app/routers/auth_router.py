from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import authenticate_user, create_access_token, get_current_user
from app.schemas import Token, UserResponse
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = create_access_token(data={"sub": user.email})
    return Token(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.get("/api-key-info")
def api_key_info():
    """Как подключаться по API-ключу (Postman, curl, скрипты). Без авторизации."""
    return {
        "message": "Для доступа по API-ключу добавьте заголовок X-API-Key с вашим ключом.",
        "header_name": "X-API-Key",
        "alternative": "Либо Authorization: Bearer <ваш_api_ключ>",
        "scope": "Полный доступ (уровень admin). Ключ задаётся в backend в переменной MEDHOUSE_API_KEY.",
        "example_curl": "curl -H \"X-API-Key: YOUR_KEY\" http://localhost:8000/api/auth/me",
    }
