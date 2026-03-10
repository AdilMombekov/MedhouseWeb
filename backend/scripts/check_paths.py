# -*- coding: utf-8 -*-
"""
Проверка по путям, которые вы указали: локальная папка «база для данных» и Google Drive (ПНЛ, Евгений, Алмас, МХ формат).
Запуск: из корня backend: python -m scripts.check_paths
"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.config import (
    DATA_BASE_DIR,
    GOOGLE_DRIVE_PNL_FOLDER_ID,
    GOOGLE_DRIVE_EVGENIJ_FOLDER_ID,
    GOOGLE_DRIVE_ALMAS_FOLDER_ID,
    GOOGLE_MX_SPREADSHEET_ID,
    GOOGLE_ZAJAVKA_FARMACEVTOV_SPREADSHEET_ID,
    GOOGLE_ZAJAVKA_SHEET_GID,
    GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE,
    BASE_DIR,
)


def check_data_base_dir():
    """Проверка папки «база для данных»."""
    print("=== Локальная папка «база для данных» ===")
    print("Путь:", DATA_BASE_DIR)
    if not DATA_BASE_DIR.exists():
        print("  [НЕТ] Папка не найдена. Создайте папку или задайте DATA_BASE_PATH в .env")
        return
    files = list(DATA_BASE_DIR.iterdir())
    if not files:
        print("  [ПУСТО] В папке нет файлов.")
        return
    expected = ["ОТЧЕТ МХК 2026.xlsx", "Номенклатура.xlsx", "Контрагент данные.xlsx", "Адреса (2).xlsx"]
    for f in sorted(files):
        name = f.name
        size = f.stat().st_size if f.is_file() else 0
        mark = "[OK]" if name in expected else ""
        print("  ", name, "(" + str(size) + " b)" if f.is_file() else "(папка)", mark)
    for e in expected:
        if not (DATA_BASE_DIR / e).exists():
            print("  [Ожидался файл]", e)
    epf = list(DATA_BASE_DIR.glob("*.epf"))
    if not epf:
        print("  [Нет .epf] Внешняя обработка 1С для ПНЛ не найдена (ожидается в этой папке).")
    else:
        for f in epf:
            print("  [OK] Обработка 1С:", f.name)
    print()


def check_google_drive():
    """Проверка доступа к папкам/таблицам в Google Drive."""
    print("=== Google Drive (указанные вами пути) ===")
    sa_path = BASE_DIR / GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE
    if not sa_path.exists():
        print("  Сервисный аккаунт не настроен:", GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE)
        print("  Положите JSON ключ в backend/ и откройте доступ к папкам для pharmacy-bot@...")
        print()
        return
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
        creds = service_account.Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
        drive = build("drive", "v3", credentials=creds)
    except Exception as e:
        print("  Ошибка инициализации Drive API:", e)
        print()
        return

    def list_folder(folder_id, label):
        if not folder_id:
            print("  ", label, ": ID не задан (GOOGLE_DRIVE_* в .env)")
            return
        try:
            q = f"'{folder_id}' in parents and trashed = false"
            res = drive.files().list(q=q, pageSize=20, fields="files(id,name,mimeType,modifiedTime)").execute()
            items = res.get("files", [])
            print("  ", label, "(" + folder_id + "):", len(items), "объектов")
            for f in items[:10]:
                print("      -", f.get("name"), "|", f.get("mimeType", ""))
            if len(items) > 10:
                print("      ... и еще", len(items) - 10)
        except Exception as e:
            print("  ", label, ": ошибка доступа —", str(e)[:80])

    list_folder(GOOGLE_DRIVE_PNL_FOLDER_ID, "Папка ПНЛ")
    list_folder(GOOGLE_DRIVE_EVGENIJ_FOLDER_ID, "Папка Евгений (Медхаус БДР)")
    list_folder(GOOGLE_DRIVE_ALMAS_FOLDER_ID, "Папка Алмас (Свисс БДР)")

    if GOOGLE_MX_SPREADSHEET_ID:
        print("  МХ формат (таблица):", GOOGLE_MX_SPREADSHEET_ID, "[OK]")
    else:
        print("  МХ формат: ID не задан (GOOGLE_MX_SPREADSHEET_ID в .env)")

    print("  Заявка фармацевты (таблица):", GOOGLE_ZAJAVKA_FARMACEVTOV_SPREADSHEET_ID, "| лист gid:", GOOGLE_ZAJAVKA_SHEET_GID)
    print()


def main():
    print("Проверка по путям (база для данных + Google Drive)\n")
    check_data_base_dir()
    check_google_drive()
    print("Готово. Задайте в backend/.env при необходимости:")
    print("  DATA_BASE_PATH, GOOGLE_DRIVE_PNL_FOLDER_ID, GOOGLE_DRIVE_EVGENIJ_FOLDER_ID,")
    print("  GOOGLE_DRIVE_ALMAS_FOLDER_ID, GOOGLE_MX_SPREADSHEET_ID,")
    print("  GOOGLE_ZAJAVKA_FARMACEVTOV_SPREADSHEET_ID, GOOGLE_ZAJAVKA_SHEET_GID")


if __name__ == "__main__":
    main()
