"""
API залогированных Google Таблиц (реестр и снимки листов).
Данные попадают в БД после запуска scripts.sync_google_sheets.
"""
from typing import Optional
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GoogleSheet, GoogleSheetSnapshot
from app.auth import get_current_user
from app.models import User
from app.logging_config import get_logger

router = APIRouter(prefix="/google-sheets", tags=["google-sheets"])
logger = get_logger(__name__)


@router.get("/list")
def list_logged_sheets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Список всех залогированных Google Таблиц (из реестра)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    rows = db.query(GoogleSheet).order_by(GoogleSheet.last_synced_at.desc().nullslast()).all()
    return {
        "total": len(rows),
        "items": [
            {
                "id": r.id,
                "spreadsheet_id": r.spreadsheet_id,
                "name": r.name,
                "folder_id": r.folder_id,
                "web_view_link": r.web_view_link,
                "sheet_count": r.sheet_count,
                "last_synced_at": r.last_synced_at.isoformat() if r.last_synced_at else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.get("/sheets/{spreadsheet_id}")
def get_spreadsheet_sheets(
    spreadsheet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Список листов одной таблицы (метаданные снимков)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    reg = db.query(GoogleSheet).filter(GoogleSheet.spreadsheet_id == spreadsheet_id).first()
    if not reg:
        logger.warning("Google Sheets: spreadsheet not in registry id=%s", spreadsheet_id)
        raise HTTPException(status_code=404, detail="Таблица не найдена в реестре. Запустите sync_google_sheets.")
    snapshots = db.query(GoogleSheetSnapshot).filter(GoogleSheetSnapshot.spreadsheet_id == spreadsheet_id).all()
    return {
        "spreadsheet_id": spreadsheet_id,
        "name": reg.name,
        "web_view_link": reg.web_view_link,
        "sheets": [
            {
                "sheet_name": s.sheet_name,
                "row_count": s.row_count,
                "col_count": s.col_count,
                "synced_at": s.synced_at.isoformat() if s.synced_at else None,
            }
            for s in snapshots
        ],
    }


@router.get("/data/{spreadsheet_id}")
def get_sheet_data(
    spreadsheet_id: str,
    sheet_name: str = Query(..., description="Имя листа (как в таблице)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    max_rows: Optional[int] = Query(None, ge=1, le=5000, description="Лимит строк (по умолчанию все)"),
):
    """Данные одного листа (залогированный снимок)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    snap = (
        db.query(GoogleSheetSnapshot)
        .filter(
            GoogleSheetSnapshot.spreadsheet_id == spreadsheet_id,
            GoogleSheetSnapshot.sheet_name == sheet_name,
        )
        .first()
    )
    if not snap:
        logger.warning("Google Sheets: sheet not found spreadsheet_id=%s sheet_name=%s", spreadsheet_id, sheet_name)
        raise HTTPException(status_code=404, detail="Лист не найден. Запустите sync_google_sheets.")
    try:
        data = json.loads(snap.data_json) if snap.data_json else []
    except Exception:
        data = []
    if max_rows:
        data = data[:max_rows]
    return {
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": sheet_name,
        "row_count": len(data),
        "col_count": max(len(row) for row in data) if data else 0,
        "synced_at": snap.synced_at.isoformat() if snap.synced_at else None,
        "values": data,
    }


@router.get("/stats")
def sheets_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Сводка: сколько таблиц и снимков залогировано."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    from sqlalchemy import func
    total_sheets = db.query(GoogleSheet).count()
    total_snapshots = db.query(GoogleSheetSnapshot).count()
    return {
        "spreadsheets_count": total_sheets,
        "snapshots_count": total_snapshots,
    }
