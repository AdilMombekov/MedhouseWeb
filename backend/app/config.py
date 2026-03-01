import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medhouse.db")

COMPANY_MEDHOUSE = os.getenv("COMPANY_MEDHOUSE", "Медхаус")
COMPANY_SWISS = os.getenv("COMPANY_SWISS", "Свисс Энерджи")

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent  # корень проекта (папка "Разработка медхаус")
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
