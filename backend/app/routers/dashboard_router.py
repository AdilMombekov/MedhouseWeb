"""
API данных для страниц дашборда. Кэш 5 мин — повторные запросы отдаются мгновенно.
"""
from pathlib import Path
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import pandas as pd
from app.database import get_db
from app.config import ANALIZ2_DIR, PROJECT_ROOT
from app.cache import cache_get, cache_set
from app.logging_config import get_logger

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = get_logger(__name__)
KATO_PATH = PROJECT_ROOT / "KATO_18.02.2026_ru.csv"


def _read_excel(path: Path, sheet=0, header=None) -> Optional[pd.DataFrame]:
    try:
        if not path.exists():
            return None
        return pd.read_excel(path, sheet_name=sheet, header=header)
    except Exception:
        return None


def _read_csv(path: Path, sep=";") -> Optional[pd.DataFrame]:
    try:
        if not path.exists():
            return None
        return pd.read_csv(path, sep=sep, encoding="utf-8")
    except Exception:
        try:
            return pd.read_csv(path, sep=sep, encoding="cp1251")
        except Exception:
            return None


def _compute_summary():
    result = {"years": [], "total_value": [], "rows_count": []}
    for year in ["2020", "2021", "2022", "2023", "2024", "2025"]:
        path = ANALIZ2_DIR / f"{year}.xlsx"
        if not path.exists():
            result["years"].append(year)
            result["total_value"].append(0)
            result["rows_count"].append(0)
            continue
        df = _read_excel(path, 0, None)
        if df is not None and not df.empty:
            num = df.select_dtypes(include=["number"])
            total = float(num.sum().sum()) if not num.empty else 0
            result["years"].append(year)
            result["total_value"].append(round(total, 2))
            result["rows_count"].append(len(df))
        else:
            result["years"].append(year)
            result["total_value"].append(0)
            result["rows_count"].append(0)
    if not result["years"]:
        logger.info("Dashboard summary: no data in ANALIZ2_DIR, returning demo aggregate")
        result = {"years": ["2020", "2021", "2022", "2023", "2024", "2025"], "total_value": [1245, 1582, 1890, 2150, 2420, 2680], "rows_count": [0] * 6}
    return result


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    cached = cache_get("dashboard:summary")
    if cached is not None:
        return cached
    out = _compute_summary()
    cache_set("dashboard:summary", out)
    return out


@router.get("/sales")
def get_sales(year: Optional[str] = Query(None), db: Session = Depends(get_db)):
    year = year or "2024"
    cache_key = f"dashboard:sales:{year}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    path = ANALIZ2_DIR / f"{year}.xlsx"
    data = []
    if path.exists():
        df = _read_excel(path, 0, 0)
        if df is not None and not df.empty:
            for _, row in df.head(100).iterrows():
                row_dict = row.dropna().to_dict()
                if row_dict:
                    data.append({str(k): (v.item() if hasattr(v, "item") else v) for k, v in row_dict.items()})
    if not data:
        data = [{"Период": f"{year}-0{i}", "Сумма": 100 * (i + 1), "Количество": 10 * i} for i in range(1, 10)]
    out = {"year": year, "items": data[:50]}
    cache_set(cache_key, out)
    return out


@router.get("/regions")
def get_regions(db: Session = Depends(get_db)):
    cached = cache_get("dashboard:regions")
    if cached is not None:
        return cached
    df = _read_csv(KATO_PATH)
    if df is None or df.empty:
        out = {"regions": [{"id": 0, "code": "—", "name": "Загрузите KATO_18.02.2026_ru.csv", "parent_id": 0}], "total": 0}
    else:
        roots = df[df["parent_id"] == 0].head(20)
        regions = []
        for _, r in roots.iterrows():
            regions.append({"id": int(r["id"]), "code": str(r.get("code", "")), "name": str(r.get("name", "")), "parent_id": int(r["parent_id"])})
        children = df[df["parent_id"].isin(roots["id"])].head(80)
        for _, r in children.iterrows():
            regions.append({"id": int(r["id"]), "code": str(r.get("code", "")), "name": str(r.get("name", "")), "parent_id": int(r["parent_id"])})
        out = {"regions": regions, "total": len(regions)}
    cache_set("dashboard:regions", out)
    return out


@router.get("/logistics")
def get_logistics(db: Session = Depends(get_db)):
    cached = cache_get("dashboard:logistics")
    if cached is not None:
        return cached
    path = ANALIZ2_DIR / "Логистика.xlsx"
    items = []
    if path.exists():
        df = _read_excel(path, 0, 0)
        if df is not None and not df.empty:
            for _, row in df.head(50).iterrows():
                items.append({str(k): (v.item() if hasattr(v, "item") else v) for k, v in row.dropna().to_dict().items()})
    if not items:
        items = [{"Склад": f"Склад {i}", "Приход": 100 * i, "Расход": 80 * i, "Остаток": 20 * i} for i in range(1, 11)]
    out = {"items": items}
    cache_set("dashboard:logistics", out)
    return out


@router.get("/products")
def get_products(year: Optional[str] = Query(None), db: Session = Depends(get_db)):
    year = year or "2024"
    cache_key = f"dashboard:products:{year}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    path = ANALIZ2_DIR / f"{year}.xlsx"
    items = []
    if path.exists():
        df = _read_excel(path, 0, 0)
        if df is not None and not df.empty:
            for _, row in df.head(60).iterrows():
                items.append({str(k): (v.item() if hasattr(v, "item") else v) for k, v in row.dropna().to_dict().items()})
    if not items:
        items = [{"Наименование": f"Товар {i}", "Группа": "Парафармация", "Кол-во": 100 * i, "Сумма": 5000 * i} for i in range(1, 16)]
    out = {"year": year, "items": items}
    cache_set(cache_key, out)
    return out


@router.get("/plan-fact")
def get_plan_fact(year: Optional[str] = Query(None), db: Session = Depends(get_db)):
    year = year or "2025"
    cache_key = f"dashboard:plan_fact:{year}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    path = ANALIZ2_DIR / f"{year}.xlsx"
    items = []
    if path.exists():
        df = _read_excel(path, 0, 0)
        if df is not None and len(df) >= 2:
            for i, row in df.head(12).iterrows():
                d = row.dropna().to_dict()
                if d:
                    items.append({str(k): (v.item() if hasattr(v, "item") else v) for k, v in d.items()})
    if not items:
        items = [{"Период": f"{year}-{str(i).zfill(2)}", "План": 2000 + i * 100, "Факт": 1800 + i * 120, "Выполнение %": round((1800 + i * 120) / (2000 + i * 100) * 100, 1)} for i in range(1, 13)]
    out = {"year": year, "items": items}
    cache_set(cache_key, out)
    return out


@router.get("/executive")
def get_executive(db: Session = Depends(get_db)):
    cached = cache_get("dashboard:executive")
    if cached is not None:
        return cached
    summary = {"years": [], "total_value": [], "rows_count": []}
    for year in ["2022", "2023", "2024", "2025"]:
        path = ANALIZ2_DIR / f"{year}.xlsx"
        if path.exists():
            df = _read_excel(path, 0, None)
            if df is not None and not df.empty:
                num = df.select_dtypes(include=["number"])
                total = float(num.sum().sum()) if not num.empty else 0
                summary["years"].append(year)
                summary["total_value"].append(round(total, 2))
                summary["rows_count"].append(len(df))
    if not summary["years"]:
        summary = {"years": ["2022", "2023", "2024", "2025"], "total_value": [1890, 2150, 2420, 2680], "rows_count": [100, 120, 130, 140]}
    out = {
        "summary": summary,
        "companies": ["Медхаус", "Свисс Энерджи"],
        "description": "Сводные показатели по годам для руководства.",
    }
    cache_set("dashboard:executive", out)
    return out
