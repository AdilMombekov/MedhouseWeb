from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app.models import User, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password,
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    if user.is_active != 1:
        return None
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    if user.is_active != 1:
        raise credentials_exception
    return user


def require_role(*allowed: Role):
    async def check(current_user: User = Depends(get_current_user)):
        if current_user is None:
            raise HTTPException(status_code=401, detail="Требуется авторизация")
        if current_user.role not in [r.value for r in allowed]:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        return current_user
    return check


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    if current_user.role != Role.admin.value:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return current_user


def require_moderator_or_admin(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    if current_user.role not in (Role.admin.value, Role.moderator.value):
        raise HTTPException(status_code=403, detail="Требуются права модератора или администратора")
    return current_user
