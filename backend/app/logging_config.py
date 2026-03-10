"""
Централизованная настройка логирования для приложения.
Уровень и вывод в файл задаются через LOG_LEVEL и LOG_FILE в .env.
"""
import logging
import sys
from pathlib import Path

from app.config import LOG_LEVEL, LOG_FILE, BASE_DIR


def setup_logging() -> None:
    """Настраивает корневой логгер и логгер приложения."""
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    format_str = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = []
    # stderr всегда
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setFormatter(logging.Formatter(format_str, datefmt=date_fmt))
    handlers.append(stderr)

    if LOG_FILE:
        path = Path(LOG_FILE)
        if not path.is_absolute():
            path = BASE_DIR / path
        path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(path, encoding="utf-8")
        fh.setFormatter(logging.Formatter(format_str, datefmt=date_fmt))
        handlers.append(fh)

    logging.basicConfig(level=level, handlers=handlers, force=True)
    # Снижаем шум от сторонних библиотек
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Возвращает логгер с заданным именем (обычно __name__)."""
    return logging.getLogger(name)
