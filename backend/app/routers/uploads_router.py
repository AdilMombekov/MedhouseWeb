import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import UPLOADS_DIR
from app.models import User, ReportUpload
from app.auth import require_moderator_or_admin, get_current_user
from app.schemas import ReportUploadResponse, ReportUploadCreate

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.get("/", response_model=list[ReportUploadResponse])
def list_uploads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    return db.query(ReportUpload).order_by(ReportUpload.created_at.desc()).all()


@router.post("/", response_model=ReportUploadResponse)
async def upload_report(
    file: UploadFile = File(...),
    report_type: str = Form(None),
    company_id: int = Form(None),
    period: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_moderator_or_admin),
):
    allowed = (".xlsx", ".xls", ".csv")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Разрешены только файлы: {', '.join(allowed)}",
        )
    unique = uuid.uuid4().hex[:8]
    stored_name = f"{unique}_{file.filename}"
    path = UPLOADS_DIR / stored_name
    with open(path, "wb") as f:
        content = await file.read()
        f.write(content)
    rec = ReportUpload(
        file_name=file.filename or stored_name,
        stored_path=str(path),
        report_type=report_type or None,
        company_id=company_id if company_id else None,
        uploaded_by_id=current_user.id,
        period=period or None,
        notes=notes or None,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return ReportUploadResponse(
        id=rec.id,
        file_name=rec.file_name,
        report_type=rec.report_type,
        company_id=rec.company_id,
        period=rec.period,
        notes=rec.notes,
        created_at=rec.created_at,
    )
