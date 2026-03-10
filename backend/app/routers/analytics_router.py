import os
from pathlib import Path
from typing import Optional, List, Any, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import pandas as pd
from app.database import get_db
from app.config import ANALIZ2_DIR
from app.cache import cache_get, cache_set
from app.models import User, AnalysisDataset, Company
from app.auth import get_current_user
from app.logging_config import get_logger

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = get_logger(__name__)
CACHE_KEY_SOURCES = "analytics:sources"
CACHE_KEY_AGGREGATE = "analytics:aggregate"
CACHE_KEY_BOOTSTRAP = "analytics:bootstrap"

# Демо-источники, если папка Анализ 2 пуста или недоступна
DEMO_SOURCES = [
    {"id": "analiz2_2020", "name": "Анализ 2 — 2020", "source": "analiz2", "period": "2020"},
    {"id": "analiz2_2021", "name": "Анализ 2 — 2021", "source": "analiz2", "period": "2021"},
    {"id": "analiz2_2022", "name": "Анализ 2 — 2022", "source": "analiz2", "period": "2022"},
    {"id": "analiz2_2023", "name": "Анализ 2 — 2023", "source": "analiz2", "period": "2023"},
    {"id": "analiz2_2024", "name": "Анализ 2 — 2024", "source": "analiz2", "period": "2024"},
    {"id": "analiz2_2025", "name": "Анализ 2 — 2025", "source": "analiz2", "period": "2025"},
]


def _safe_read_excel(path: Path, sheet: Optional[int] = 0, header: Optional[int] = None) -> Optional[pd.DataFrame]:
    try:
        if not path.exists():
            return None
        df = pd.read_excel(path, sheet_name=sheet, header=header)
        return df
    except Exception as e:
        logger.debug("Failed to read excel %s: %s", path, e)
        return None


def _excel_numeric_total(path: Path) -> Tuple[float, int]:
    """Сумма по всем числовым колонкам и число строк. Пробует с заголовком и без."""
    for use_header in (0, None):
        df = _safe_read_excel(path, 0, use_header)
        if df is None or df.empty:
            continue
        numeric = df.select_dtypes(include=["number"])
        if not numeric.empty:
            total = float(numeric.sum().sum())
            return (total, len(df))
        # если числовых колонок нет — считаем объём по количеству строк
        if len(df) > 0:
            return (float(len(df) * 100), len(df))
    return (0.0, 0)


def _compute_sources() -> list:
    sources = []
    if ANALIZ2_DIR.exists():
        for f in sorted(ANALIZ2_DIR.glob("*.xlsx")):
            name = f.stem
            if name.isdigit() and len(name) == 4:
                sources.append({"id": f"analiz2_{name}", "name": f"Анализ 2 — {name}", "source": "analiz2", "period": name})
            else:
                sources.append({"id": f"analiz2_{f.stem}", "name": f"Анализ 2 — {f.stem}", "source": "analiz2"})
    if not sources:
        sources = DEMO_SOURCES.copy()
    return sources


@router.get("/sources")
def list_analytics_sources(db: Session = Depends(get_db)):
    """Список источников данных (с кэшем)."""
    cached = cache_get(CACHE_KEY_SOURCES)
    if cached is not None:
        return {"sources": cached}
    sources = _compute_sources()
    cache_set(CACHE_KEY_SOURCES, sources)
    return {"sources": sources}


@router.get("/preview")
def preview_dataset(
    source_id: str = Query(..., description="analiz2_2024 или analiz2_Логистика"),
    sheet: int = Query(0, ge=0),
    rows: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Превью таблицы (с кэшем по source_id)."""
    if not source_id.startswith("analiz2_"):
        logger.warning("Analytics preview: unsupported source_id=%s", source_id)
        raise HTTPException(status_code=400, detail="Поддерживается только источник analiz2_*")
    cache_key = f"analytics:preview:{source_id}:{sheet}:{rows}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    key = source_id.replace("analiz2_", "")
    path = ANALIZ2_DIR / f"{key}.xlsx"
    if not path.exists():
        out = {"columns": ["Период", "Показатель", "Значение"], "rows": [[key, "Загрузите файл в папку «Анализ 2»", "—"]]}
    else:
        df = _safe_read_excel(path, sheet, header=None)
        if df is None:
            logger.warning("Analytics preview: failed to read file path=%s", path)
            raise HTTPException(status_code=422, detail="Не удалось прочитать файл")
        df = df.head(rows)
        out = {"columns": list(df.columns.astype(str)), "rows": df.fillna("").values.tolist()}
    cache_set(cache_key, out)
    return out


# Демо-данные для графика, если нет реальных файлов
DEMO_AGGREGATE = [
    {"period": "2020", "value": 1245000, "rows": 0},
    {"period": "2021", "value": 1582000, "rows": 0},
    {"period": "2022", "value": 1890000, "rows": 0},
    {"period": "2023", "value": 2150000, "rows": 0},
    {"period": "2024", "value": 2420000, "rows": 0},
    {"period": "2025", "value": 2680000, "rows": 0},
]


def _compute_aggregate(years_str: str = "2020,2021,2022,2023,2024,2025"):
    result = []
    year_list = [y.strip() for y in years_str.split(",") if y.strip()]
    if ANALIZ2_DIR.exists():
        for y in year_list:
            path = ANALIZ2_DIR / f"{y}.xlsx"
            if not path.exists():
                continue
            total, rows = _excel_numeric_total(path)
            if rows > 0:
                result.append({"period": y, "value": round(total, 2), "rows": rows})
    if not result:
        result = [d for d in DEMO_AGGREGATE if d["period"] in year_list]
        if not result:
            result = DEMO_AGGREGATE.copy()
    from_real = any(r.get("rows", 0) > 0 for r in result)
    return {
        "data": result,
        "meta": {
            "metric": "year",
            "description": "Сумма числовых полей по году из файлов Анализ 2" if from_real
                else "Демо-показатели (загрузите файлы 2020–2025.xlsx в папку «Анализ 2» для реальных данных)",
        },
    }


@router.get("/aggregate")
def aggregate_analiz2(
    metric: str = Query("year", description="year | city | product"),
    years: Optional[str] = Query(None, description="2022,2023,2024"),
    db: Session = Depends(get_db),
):
    """Агрегаты по годам (с кэшем)."""
    years_str = years or "2020,2021,2022,2023,2024,2025"
    cache_key = f"{CACHE_KEY_AGGREGATE}:{years_str}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    out = _compute_aggregate(years_str)
    cache_set(cache_key, out)
    return out


@router.get("/bootstrap")
def analytics_bootstrap(db: Session = Depends(get_db)):
    """Всё для главной страницы за один запрос: sources + aggregate (кэш 5 мин)."""
    cached = cache_get(CACHE_KEY_BOOTSTRAP)
    if cached is not None:
        return cached
    sources = _compute_sources()
    aggregate = _compute_aggregate("2020,2021,2022,2023,2024,2025")
    out = {"sources": sources, "aggregate": aggregate}
    cache_set(CACHE_KEY_BOOTSTRAP, out)
    return out
