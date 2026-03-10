"""
Однократная инициализация БД для прода (Supabase/Railway).
Выполняет init_db и create_dashboard_templates.
Запуск: из папки backend с заданным DATABASE_URL (Postgres).

  set DATABASE_URL=postgresql://...
  python -m scripts.init_production_db

Или на Railway: One-off run с переменной DATABASE_URL.
"""
import os
import sys
from pathlib import Path

backend = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend))

def main():
    url = os.environ.get("DATABASE_URL", "")
    if "sqlite" in url and "medhouse.db" in url:
        print("Предупреждение: DATABASE_URL указывает на SQLite (локальная БД).")
        print("Для прода задайте Postgres connection string (Supabase → Settings → Database).")
        answer = input("Продолжить инициализацию SQLite? [y/N]: ").strip().lower()
        if answer != "y":
            sys.exit(1)

    print("Запуск init_db...")
    from scripts import init_db
    init_db.main()

    print("Запуск create_dashboard_templates...")
    from scripts import create_dashboard_templates
    create_dashboard_templates.main()

    print("Готово. БД и шаблоны инициализированы.")

if __name__ == "__main__":
    main()
