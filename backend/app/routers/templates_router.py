import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import TEMPLATES_DIR
from app.models import User, ReportTemplate
from app.auth import require_moderator_or_admin, get_current_user
from app.schemas import ReportTemplateResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=list[ReportTemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    return db.query(ReportTemplate).all()


@router.get("/download/{template_id}")
def download_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    t = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    path = TEMPLATES_DIR / t.file_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Файл шаблона не найден на сервере")
    return FileResponse(
        path,
        filename=t.file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/download-by-type/{report_type}")
def download_template_by_type(
    report_type: str,
    db: Session = Depends(get_db),
):
    """Скачать шаблон по коду типа (например dashboard_summary)."""
    t = db.query(ReportTemplate).filter(ReportTemplate.report_type == report_type).first()
    if not t:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    path = TEMPLATES_DIR / t.file_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Файл шаблона не найден на сервере")
    return FileResponse(
        path,
        filename=t.file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
