import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Логирование: уровень DEBUG|INFO|WARNING|ERROR, опционально файл (путь или пусто)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "").strip()  # например backend/logs/app.log

# CORS: в проде задайте CORS_ORIGINS через запятую (например https://medhouse.vercel.app); пусто или * — разрешить все (для разработки)
_cors_raw = os.getenv("CORS_ORIGINS", "").strip()
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()] if _cors_raw else ["*"]

_raw_db = (os.getenv("DATABASE_URL") or "").strip()
DATABASE_URL = _raw_db if _raw_db else "sqlite:///./medhouse.db"

# Supabase (опционально): URL и ключи для клиента/будущих фич. Для БД используется Postgres connection string в DATABASE_URL (Supabase → Settings → Database).
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

COMPANY_MEDHOUSE = os.getenv("COMPANY_MEDHOUSE", "Медхаус")
COMPANY_SWISS = os.getenv("COMPANY_SWISS", "Свисс Энерджи")

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent  # корень проекта (папка "Разработка медхаус")
# Папка «база для данных» — вы указали: ОТЧЕТ МХК 2026, Номенклатура, Контрагент данные, Адреса (2)
DATA_BASE_DIR = Path(os.getenv("DATA_BASE_PATH", str(PROJECT_ROOT / "база для данных")))
ANALIZ2_DIR = Path(os.getenv("ANALIZ2_PATH", str(PROJECT_ROOT / "Анализ 2")))
UPLOADS_DIR = BASE_DIR / "uploads"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# API-ключи для доступа из Postman, curl и сторонних программ (полный доступ как admin)
# Поддерживаются: MEDHOUSE_API_KEY или MEDHOUSE_API_KEY_1, _2, _3 (любой из них действителен)
def _collect_api_keys():
    keys = []
    for name in ("MEDHOUSE_API_KEY", "MEDHOUSE_API_KEY_1", "MEDHOUSE_API_KEY_2", "MEDHOUSE_API_KEY_3"):
        v = os.getenv(name, "").strip()
        if v:
            keys.append(v)
    return keys

API_KEYS = _collect_api_keys()

# Google Drive
GOOGLE_DRIVE_CREDENTIALS_FILE = os.getenv("GOOGLE_DRIVE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_DRIVE_TOKEN_FILE = os.getenv("GOOGLE_DRIVE_TOKEN_FILE", "token.json")
# Сервисный аккаунт (pharmacy-bot@pharmacy-bot-487900.iam.gserviceaccount.com) — без OAuth в браузере
GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE", "service_account_pharmacy_bot.json")
# Папка для вкладки ПНЛ на сайте (полный доступ выдан сервисному аккаунту)
# Ссылка: https://drive.google.com/drive/folders/1f-3_NyHFIRBGtXf8-aoJBy4yjtNYN6rx
GOOGLE_DRIVE_PNL_FOLDER_ID = os.getenv("GOOGLE_DRIVE_PNL_FOLDER_ID", "1f-3_NyHFIRBGtXf8-aoJBy4yjtNYN6rx")
# Формат бюджета (БДР) лежит в папках, в названии которых в конце «Евгений» (Медхаус) или «Алмас» (Свисс)
GOOGLE_DRIVE_EVGENIJ_FOLDER_ID = os.getenv("GOOGLE_DRIVE_EVGENIJ_FOLDER_ID", "")   # папка ...Евгений
GOOGLE_DRIVE_ALMAS_FOLDER_ID = os.getenv("GOOGLE_DRIVE_ALMAS_FOLDER_ID", "")       # папка ...Алмас
# МХ формат — книга Google Sheets: реал 8 мес, Продажи дистр, Касса, Банк, Оста, Дзад и т.д.
# https://docs.google.com/spreadsheets/d/1G5atWyRUOxr23iZ3Q8txMRo_DrdjdCEo9VVQfVBAl6Q/edit?gid=1011251887
GOOGLE_MX_SPREADSHEET_ID = os.getenv("GOOGLE_MX_SPREADSHEET_ID", "1G5atWyRUOxr23iZ3Q8txMRo_DrdjdCEo9VVQfVBAl6Q")
# Форма «Заявка фармацевты» — таблица для остатков от ТП/сетей
GOOGLE_ZAJAVKA_FARMACEVTOV_SPREADSHEET_ID = os.getenv("GOOGLE_ZAJAVKA_FARMACEVTOV_SPREADSHEET_ID", "1XSFq5PbJadJR21h6Z9z3hhfnGu4tEl93K6WEXUYutdI")
GOOGLE_ZAJAVKA_SHEET_GID = os.getenv("GOOGLE_ZAJAVKA_SHEET_GID", "1144561640")
