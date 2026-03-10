# -*- coding: utf-8 -*-
"""
Обнаружение всех Google Таблиц, доступных сервисному аккаунту, и логирование в БД.
Запуск: python -m scripts.sync_google_sheets
Ищет таблицы: в папке ПНЛ, затем все файлы типа spreadsheet, к которым есть доступ.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal
from app.models import Base, GoogleSheet, GoogleSheetSnapshot
from app.database import engine
from app.config import BASE_DIR, GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE, GOOGLE_DRIVE_PNL_FOLDER_ID

Base.metadata.create_all(bind=engine)

SERVICE_ACCOUNT_PATH = BASE_DIR / GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def _get_creds():
    if SERVICE_ACCOUNT_PATH.exists():
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(str(SERVICE_ACCOUNT_PATH), scopes=SCOPES)
    if not CREDENTIALS_PATH.exists():
        return None
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def _discover_spreadsheets(drive_service, folder_id=None):
    """Список всех Google Таблиц в папке или всех доступных."""
    q = "trashed = false and mimeType = 'application/vnd.google-apps.spreadsheet'"
    if folder_id:
        q += f" and '{folder_id}' in parents"
    else:
        q += " and 'root' in parents"
    files = []
    page_token = None
    while True:
        r = drive_service.files().list(
            q=q,
            pageSize=100,
            fields="nextPageToken, files(id, name, parents, webViewLink)",
            orderBy="modifiedTime desc",
            pageToken=page_token,
        ).execute()
        files.extend(r.get("files", []))
        page_token = r.get("nextPageToken")
        if not page_token:
            break
    return files


def _discover_all_shared_spreadsheets(drive_service):
    """Все таблицы, к которым у аккаунта есть доступ (без фильтра по папке — только mimeType)."""
    q = "trashed = false and mimeType = 'application/vnd.google-apps.spreadsheet'"
    files = []
    page_token = None
    while True:
        r = drive_service.files().list(
            q=q,
            pageSize=100,
            fields="nextPageToken, files(id, name, parents, webViewLink)",
            orderBy="modifiedTime desc",
            pageToken=page_token,
            supportsAllDrives=True,
        ).execute()
        files.extend(r.get("files", []))
        page_token = r.get("nextPageToken")
        if not page_token:
            break
    return files


def _get_sheet_names(sheets_service, spreadsheet_id):
    """Метаданные таблицы: список листов."""
    try:
        meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return [
            (s["properties"]["title"], s["properties"].get("gridProperties", {}).get("rowCount", 0), s["properties"].get("gridProperties", {}).get("columnCount", 0))
            for s in meta.get("sheets", [])
        ]
    except Exception:
        return []


def _get_sheet_values(sheets_service, spreadsheet_id, sheet_name, max_rows=10000):
    """Данные листа (значения)."""
    try:
        r = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!A1:ZZ{min(max_rows, 5000)}",
        ).execute()
        return r.get("values", [])
    except Exception:
        return []


def main():
    creds = _get_creds()
    if not creds:
        print("Нет учётных данных. Положите service_account_pharmacy_bot.json или credentials.json в backend.")
        return 1

    from googleapiclient.discovery import build
    drive_service = build("drive", "v3", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)

    # 1) Все таблицы, доступные аккаунту (в т.ч. расшаренные)
    all_files = _discover_all_shared_spreadsheets(drive_service)
    # 2) Плюс таблицы в папке ПНЛ (если не попали в общий список)
    pnl_files = _discover_spreadsheets(drive_service, GOOGLE_DRIVE_PNL_FOLDER_ID)
    seen = {f["id"] for f in all_files}
    for f in pnl_files:
        if f["id"] not in seen:
            seen.add(f["id"])
            all_files.append(f)

    print(f"Найдено таблиц: {len(all_files)}")

    db = SessionLocal()
    try:
        for f in all_files:
            sid = f["id"]
            name = f.get("name", "")
            folder_id = f.get("parents", [None])[0] if f.get("parents") else None
            web_link = f.get("webViewLink", "")

            sheet_meta = _get_sheet_names(sheets_service, sid)
            if not sheet_meta:
                print(f"  Пропуск {name} ({sid}): нет листов или нет доступа")
                continue

            rec = db.query(GoogleSheet).filter(GoogleSheet.spreadsheet_id == sid).first()
            if not rec:
                rec = GoogleSheet(
                    spreadsheet_id=sid,
                    name=name,
                    folder_id=folder_id,
                    web_view_link=web_link,
                    sheet_count=len(sheet_meta),
                )
                db.add(rec)
            else:
                rec.name = name
                rec.folder_id = folder_id
                rec.web_view_link = web_link
                rec.sheet_count = len(sheet_meta)
            rec.last_synced_at = datetime.utcnow()
            db.commit()
            db.refresh(rec)

            # Удаляем старые снимки этого spreadsheet
            db.query(GoogleSheetSnapshot).filter(GoogleSheetSnapshot.spreadsheet_id == sid).delete()
            db.commit()

            for sheet_name, row_count, col_count in sheet_meta:
                values = _get_sheet_values(sheets_service, sid, sheet_name)
                rows = len(values)
                cols = max(len(row) for row in values) if values else 0
                snap = GoogleSheetSnapshot(
                    spreadsheet_id=sid,
                    sheet_name=sheet_name,
                    row_count=rows,
                    col_count=cols,
                    data_json=json.dumps(values, ensure_ascii=False),
                    synced_at=datetime.utcnow(),
                )
                db.add(snap)
                print(f"  {name} / {sheet_name}: {rows} x {cols}")
            db.commit()

        total_sheets = db.query(GoogleSheet).count()
        total_snapshots = db.query(GoogleSheetSnapshot).count()
        print(f"Готово. В реестре таблиц: {total_sheets}, снимков листов: {total_snapshots}")
    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")
        raise
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
