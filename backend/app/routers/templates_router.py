import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import TEMPLATES_DIR
from app.models import User, ReportTemplate
from app.auth import require_moderator_or_admin, get_current_user
from app.schemas import ReportTemplateResponse
from app.logging_config import get_logger

router = APIRouter(prefix="/templates", tags=["templates"])
logger = get_logger(__name__)


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
        logger.warning("Template download: not found id=%s", template_id)
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    path = TEMPLATES_DIR / t.file_name
    if not path.exists():
        logger.warning("Template download: file missing id=%s path=%s", template_id, path)
        raise HTTPException(status_code=404, detail="Файл шаблона не найден на сервере")
    logger.info("Template download: id=%s file=%s", template_id, t.file_name)
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
        logger.warning("Template download-by-type: not found type=%s", report_type)
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    path = TEMPLATES_DIR / t.file_name
    if not path.exists():
        logger.warning("Template download-by-type: file missing type=%s path=%s", report_type, path)
        raise HTTPException(status_code=404, detail="Файл шаблона не найден на сервере")
    logger.info("Template download-by-type: type=%s file=%s", report_type, t.file_name)
    return FileResponse(
        path,
        filename=t.file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
