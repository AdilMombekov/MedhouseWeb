import logging
import threading
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import engine, Base
from app.routers import auth_router, users_router, companies_router, templates_router, uploads_router, analytics_router, google_drive_router, google_sheets_router, dashboard_router, mailing_router, map_router
from app.cache import cache_set
from app.logging_config import setup_logging, get_logger
from app.config import CORS_ORIGINS

setup_logging()
logger = get_logger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medhouse / Swiss Energy — Управленческая отчётность",
    description="Дашборд и API для отчётности Медхаус (дистрибьютор) и Свисс Энерджи (контролирующая компания).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Логирует каждый HTTP-запрос: метод, путь, статус, длительность, client IP."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        client = request.client.host if request.client else "?"
        method = request.method
        path = request.url.path
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        except Exception:
            logger.exception("Request failed: %s %s", method, path)
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "%s %s %s %.1fms client=%s",
                method,
                path,
                status,
                duration_ms,
                client,
            )


app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth_router.router, prefix="/api")
app.include_router(users_router.router, prefix="/api")
app.include_router(companies_router.router, prefix="/api")
app.include_router(templates_router.router, prefix="/api")
app.include_router(uploads_router.router, prefix="/api")
app.include_router(analytics_router.router, prefix="/api")
app.include_router(google_drive_router.router, prefix="/api")
app.include_router(google_sheets_router.router, prefix="/api")
app.include_router(dashboard_router.router, prefix="/api")
app.include_router(mailing_router.router, prefix="/api")
app.include_router(map_router.router, prefix="/api")


def _warm_cache():
    """Прогрев кэша при старте — первый заход пользователя будет быстрым."""
    try:
        from app.routers.analytics_router import _compute_sources, _compute_aggregate
        from app.routers.analytics_router import CACHE_KEY_BOOTSTRAP
        sources = _compute_sources()
        aggregate = _compute_aggregate("2020,2021,2022,2023,2024,2025")
        cache_set(CACHE_KEY_BOOTSTRAP, {"sources": sources, "aggregate": aggregate})
        logger.info("Cache warm-up done: %s sources, aggregate ready", len(sources))
    except Exception as e:
        logger.warning("Cache warm-up failed: %s", e, exc_info=True)


@app.on_event("startup")
def startup():
    logger.info("Application starting")
    threading.Thread(target=_warm_cache, daemon=True).start()


@app.get("/")
def root():
    return {"message": "Medhouse / Swiss Energy API", "docs": "/docs"}


@app.get("/health")
def health():
    """Простая проверка: сервис отвечает."""
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    """Readiness: сервис и БД доступны (для Railway/K8s)."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning("Health ready failed: %s", e)
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "detail": "Database unavailable"},
        )
    return {"status": "ok", "database": "connected"}
