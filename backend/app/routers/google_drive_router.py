import os
from pathlib import Path
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from app.config import (
    BASE_DIR,
    GOOGLE_DRIVE_CREDENTIALS_FILE,
    GOOGLE_DRIVE_TOKEN_FILE,
    GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE,
    GOOGLE_DRIVE_PNL_FOLDER_ID,
)
from app.models import User
from app.auth import get_current_user
from app.logging_config import get_logger

router = APIRouter(prefix="/google-drive", tags=["google-drive"])
logger = get_logger(__name__)

CREDENTIALS_PATH = BASE_DIR / GOOGLE_DRIVE_CREDENTIALS_FILE
TOKEN_PATH = BASE_DIR / GOOGLE_DRIVE_TOKEN_FILE
SERVICE_ACCOUNT_PATH = BASE_DIR / GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE
SCOPES_DRIVE = ["https://www.googleapis.com/auth/drive.readonly"]
SCOPES_SHEETS = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SCOPES = list(dict.fromkeys(SCOPES_DRIVE + SCOPES_SHEETS))


def _get_google_creds():
    """Общие учётные данные для Drive и Sheets (сервисный аккаунт или OAuth)."""
    if SERVICE_ACCOUNT_PATH.exists():
        try:
            from google.oauth2 import service_account
            return service_account.Credentials.from_service_account_file(
                str(SERVICE_ACCOUNT_PATH), scopes=SCOPES
            )
        except Exception as e:
            logger.debug("Service account creds failed: %s", e)
    if not CREDENTIALS_PATH.exists():
        return None
    try:
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
    except Exception as e:
        logger.debug("OAuth creds failed: %s", e)
        return None


def _get_drive_service():
    """Сервис Google Drive."""
    creds = _get_google_creds()
    if not creds:
        return None
    try:
        from googleapiclient.discovery import build
        return build("drive", "v3", credentials=creds)
    except Exception:
        return None


def _get_sheets_service():
    """Сервис Google Sheets (те же учётные данные)."""
    creds = _get_google_creds()
    if not creds:
        return None
    try:
        from googleapiclient.discovery import build
        return build("sheets", "v4", credentials=creds)
    except Exception:
        return None


@router.get("/status")
def drive_status():
    """Проверка: подключён ли Google Drive (сервисный аккаунт или OAuth)."""
    has_sa = SERVICE_ACCOUNT_PATH.exists()
    has_creds = CREDENTIALS_PATH.exists()
    has_token = TOKEN_PATH.exists()
    service = _get_drive_service()
    return {
        "connected": service is not None,
        "auth_type": "service_account" if has_sa else ("oauth" if has_creds else None),
        "has_service_account_file": has_sa,
        "has_credentials": has_creds,
        "has_token": has_token,
        "pnl_folder_id": GOOGLE_DRIVE_PNL_FOLDER_ID,
        "message": "Сервисный аккаунт: положите service_account_pharmacy_bot.json в backend и откройте папку ПНЛ для сервисного аккаунта."
        if not has_creds and not has_sa else ("Готово к чтению файлов." if service else "Требуется повторная авторизация или доступ к папке ПНЛ для сервисного аккаунта."),
    }


@router.get("/files")
def list_drive_files(
    folder_id: Optional[str] = Query(None, description="ID папки на Google Drive"),
    current_user: User = Depends(get_current_user),
):
    """Список файлов в папке Google Drive (или в корне)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    service = _get_drive_service()
    if not service:
        raise HTTPException(
            status_code=503,
            detail="Google Drive не настроен. Положите credentials.json в папку backend и перезапустите.",
        )
    try:
        q = "trashed = false"
        if folder_id:
            q += f" and '{folder_id}' in parents"
        else:
            q += " and 'root' in parents"
        results = service.files().list(
            q=q,
            pageSize=50,
            fields="files(id, name, mimeType, modifiedTime, size)",
            orderBy="modifiedTime desc",
        ).execute()
        files = results.get("files", [])
        return {"files": files}
    except Exception as e:
        logger.error("Google Drive list files failed: folder_id=%s error=%s", folder_id, e)
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/read")
def read_drive_file(
    file_id: str = Query(..., description="ID файла на Google Drive"),
    current_user: User = Depends(get_current_user),
):
    """Скачать содержимое файла с Google Drive (для импорта в систему)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    service = _get_drive_service()
    if not service:
        raise HTTPException(status_code=503, detail="Google Drive не настроен.")
    try:
        import io
        from googleapiclient.http import MediaIoBaseDownload

        request = service.files().get_media(fileId=file_id)
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        buf.seek(0)
        # Возвращаем как base64 или сохраняем во временный файл — здесь упрощённо возвращаем размер
        return {"file_id": file_id, "size": len(buf.getvalue()), "message": "Файл получен. Используйте импорт по file_id для загрузки в отчётность."}
    except Exception as e:
        logger.error("Google Drive read file failed: file_id=%s error=%s", file_id, e)
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/pnl")
def list_pnl_folder(
    folder_id: Optional[str] = Query(None, description="ID папки (по умолчанию — папка ПНЛ для вкладки сайта)"),
    page_size: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
):
    """
    Список файлов и подпапок в папке ПНЛ на Google Drive.
    Для будущей вкладки «ПНЛ» на сайте. Папка: https://drive.google.com/drive/folders/1f-3_NyHFIRBGtXf8-aoJBy4yjtNYN6rx
    Доступ: выдан полный доступ сервисному аккаунту pharmacy-bot@pharmacy-bot-487900.iam.gserviceaccount.com.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    service = _get_drive_service()
    if not service:
        raise HTTPException(
            status_code=503,
            detail="Google Drive не настроен. Используйте service_account_pharmacy_bot.json или credentials.json.",
        )
    target_id = folder_id or GOOGLE_DRIVE_PNL_FOLDER_ID
    try:
        # Метаданные самой папки
        folder_meta = service.files().get(
            fileId=target_id,
            fields="id, name, mimeType, modifiedTime, createdTime",
        ).execute()
        # Файлы и папки внутри
        q = f"'{target_id}' in parents and trashed = false"
        results = service.files().list(
            q=q,
            pageSize=page_size,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
            orderBy="modifiedTime desc",
        ).execute()
        files = results.get("files", [])
        # Папки в начало (для вкладки ПНЛ удобнее)
        files.sort(key=lambda f: (0 if f.get("mimeType") == "application/vnd.google-apps.folder" else 1, f.get("name", "")))
        return {
            "folder": {
                "id": folder_meta.get("id"),
                "name": folder_meta.get("name"),
                "mimeType": folder_meta.get("mimeType"),
                "modifiedTime": folder_meta.get("modifiedTime"),
                "createdTime": folder_meta.get("createdTime"),
            },
            "items": files,
            "total": len(files),
            "folder_id": target_id,
            "pnl_folder_url": f"https://drive.google.com/drive/folders/{GOOGLE_DRIVE_PNL_FOLDER_ID}",
        }
    except Exception as e:
        logger.error("Google Drive PNL folder failed: folder_id=%s error=%s", target_id, e)
        raise HTTPException(status_code=502, detail=str(e))
