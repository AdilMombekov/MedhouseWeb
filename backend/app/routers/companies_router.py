from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas import CompanyResponse
from app.models import Company

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=list[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()
