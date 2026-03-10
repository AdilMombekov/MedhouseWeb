"""
API рассылки из 1С: партии и строки, залогированные в БД.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database import get_db
from app.models import MailingBatch, MailingRow
from app.auth import get_current_user

router = APIRouter(prefix="/mailing", tags=["mailing"])


@router.get("/batches")
def list_batches(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Список загруженных партий рассылки (последние сначала)."""
    batches = db.query(MailingBatch).order_by(desc(MailingBatch.created_at)).limit(50).all()
    return {
        "items": [
            {
                "id": b.id,
                "source_file": b.source_file,
                "sheet_name": b.sheet_name,
                "row_count": b.row_count,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in batches
        ],
    }


@router.get("/rows")
def list_rows(
    batch_id: Optional[int] = Query(None, description="Фильтр по партии"),
    organization: Optional[str] = Query(None, description="Организация (MedHouse)"),
    period_date: Optional[str] = Query(None, description="Период дата, например 04.03.2026"),
    kontragent: Optional[str] = Query(None, description="Часть имени контрагента"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Строки рассылки с фильтрами. По умолчанию — последняя партия."""
    q = db.query(MailingRow)
    if batch_id is not None:
        q = q.filter(MailingRow.batch_id == batch_id)
    else:
        # последняя партия
        last_batch = db.query(MailingBatch).order_by(desc(MailingBatch.created_at)).first()
        if last_batch:
            q = q.filter(MailingRow.batch_id == last_batch.id)
    if organization:
        q = q.filter(MailingRow.organization.ilike(f"%{organization}%"))
    if period_date:
        q = q.filter(MailingRow.period_date == period_date)
    if kontragent:
        q = q.filter(MailingRow.kontragent.ilike(f"%{kontragent}%"))

    total = q.count()
    rows = q.order_by(MailingRow.row_index).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": r.id,
                "batch_id": r.batch_id,
                "row_index": r.row_index,
                "period_date": r.period_date,
                "organization": r.organization,
                "kontragent": r.kontragent,
                "nomerklatura": r.nomerklatura,
                "amount": r.amount,
                "profit": r.profit,
                "raw_data": r.raw_data,
            }
            for r in rows
        ],
    }


@router.get("/stats")
def mailing_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Сводка по рассылке: кол-во партий, строк, последняя дата."""
    batches_count = db.query(func.count(MailingBatch.id)).scalar() or 0
    rows_count = db.query(func.count(MailingRow.id)).scalar() or 0
    last_batch = db.query(MailingBatch).order_by(desc(MailingBatch.created_at)).first()
    return {
        "batches_count": batches_count,
        "rows_count": rows_count,
        "last_batch": {
            "id": last_batch.id,
            "source_file": last_batch.source_file,
            "row_count": last_batch.row_count,
            "created_at": last_batch.created_at.isoformat() if last_batch and last_batch.created_at else None,
        } if last_batch else None,
    }
