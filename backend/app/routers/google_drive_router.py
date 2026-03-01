import os
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models import User
from app.auth import get_current_user

router = APIRouter(prefix="/google-drive", tags=["google-drive"])

# Опциональная интеграция: если нет credentials — эндпоинты вернут инструкцию
CREDENTIALS_PATH = Path(__file__).resolve().parent.parent.parent / "credentials.json"
TOKEN_PATH = Path(__file__).resolve().parent.parent.parent / "token.json"


def _get_drive_service():
    """Получить сервис Google Drive при наличии credentials."""
    if not CREDENTIALS_PATH.exists():
        return None
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
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
        return build("drive", "v3", credentials=creds)
    except Exception:
        return None


@router.get("/status")
def drive_status():
    """Проверка: подключён ли Google Drive."""
    has_creds = CREDENTIALS_PATH.exists()
    has_token = TOKEN_PATH.exists()
    service = _get_drive_service() if has_creds else None
    return {
        "connected": service is not None,
        "has_credentials": has_creds,
        "has_token": has_token,
        "message": "Подключите credentials.json и при первом запросе пройдите OAuth в браузере."
        if not has_creds else ("Готово к чтению файлов." if service else "Требуется повторная авторизация."),
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
        raise HTTPException(status_code=502, detail=str(e))
