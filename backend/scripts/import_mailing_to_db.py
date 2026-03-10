# -*- coding: utf-8 -*-
"""
Импорт рассылки из 1С (файл «Выгрузка XLSX (2).xlsx») в БД.
Запуск: python -m scripts.import_mailing_to_db
Ищет файл в корне проекта по шаблону имени "XLSX (2)".
"""
import sys
import json
from pathlib import Path
from datetime import datetime

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal
from app.models import Base, MailingBatch, MailingRow
from app.database import engine

# создать таблицы, если ещё нет
Base.metadata.create_all(bind=engine)


def _find_mailing_file():
    candidates = list(PROJECT_ROOT.glob("*.xlsx"))
    for f in candidates:
        if "XLSX (2)" in f.name:
            return f
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def _safe_float(v):
    if v is None or (isinstance(v, float) and __import__("math").isnan(v)):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_str(v, max_len=512):
    if v is None or (isinstance(v, float) and __import__("math").isnan(v)):
        return None
    s = str(v).strip()
    return s[:max_len] if s else None


def main():
    target = _find_mailing_file()
    if not target or not target.exists():
        print("Файл рассылки (Выгрузка XLSX (2).xlsx) не найден в корне проекта.")
        return 1

    import pandas as pd

    xl = pd.ExcelFile(target)
    sheet_name = xl.sheet_names[0] if xl.sheet_names else "Лист_1"
    df = pd.read_excel(target, sheet_name=sheet_name, header=0)

    # маппинг колонок (русские названия из 1С)
    col_map = {}
    for i, c in enumerate(df.columns):
        col_map[i] = str(c).strip()

    # индексы ключевых полей по имени
    def find_col(substr):
        for i, name in col_map.items():
            if substr in name:
                return i
        return None

    idx_nomerklatura = 0
    idx_organization = find_col("Организация") or 1
    idx_period = find_col("Период дата") or 2
    idx_kontragent = find_col("Контрагент") or 4
    idx_amount = find_col("Сумма продажи")  # Сумма продажи (в единицах)
    idx_profit = find_col("Profit") or (len(df.columns) - 1)

    db = SessionLocal()
    try:
        batch = MailingBatch(
            source_file=target.name,
            sheet_name=sheet_name,
            row_count=0,
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        print(f"Создана партия рассылки id={batch.id}, файл={target.name}, лист={sheet_name}")

        inserted = 0
        for i, row in df.iterrows():
            vals = row.tolist()
            raw = {}
            for j, v in enumerate(vals):
                key = col_map.get(j, f"col_{j}")
                if pd.isna(v):
                    raw[key] = None
                elif isinstance(v, (int, float)):
                    raw[key] = v
                else:
                    raw[key] = str(v).strip() or None

            # пропускаем итоговую строку (все пустые или "Итого")
            if i == len(df) - 1 and all(pd.isna(v) or str(v).strip() in ("", "Итого") for v in vals[:5]):
                continue

            period_date = _safe_str(row.iloc[idx_period] if idx_period is not None else None, 20)
            organization = _safe_str(row.iloc[idx_organization] if idx_organization is not None else None, 100)
            kontragent = _safe_str(row.iloc[idx_kontragent] if idx_kontragent is not None else None, 255)
            nomerklatura = _safe_str(row.iloc[idx_nomerklatura], 512)
            amount = _safe_float(row.iloc[idx_amount]) if idx_amount is not None else None
            profit = _safe_float(row.iloc[idx_profit]) if idx_profit is not None else None

            mr = MailingRow(
                batch_id=batch.id,
                row_index=int(i) + 1,
                period_date=period_date,
                organization=organization,
                kontragent=kontragent,
                nomerklatura=nomerklatura,
                amount=amount,
                profit=profit,
                raw_data=json.dumps(raw, ensure_ascii=False),
            )
            db.add(mr)
            inserted += 1
            if inserted % 1000 == 0:
                db.commit()
                print(f"  импортировано строк: {inserted}")

        batch.row_count = inserted
        db.commit()
        print(f"Готово. Всего строк в БД: {inserted}, batch_id={batch.id}")
    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")
        raise
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
