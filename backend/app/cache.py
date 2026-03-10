"""
Простой in-memory кэш с TTL. Ускоряет ответы: Excel/CSV не читаются при каждом запросе.
"""
import time
from typing import Any, Optional

_CACHE: dict[str, tuple[Any, float]] = {}
TTL_SECONDS = 300  # 5 минут


def cache_get(key: str) -> Optional[Any]:
    if key not in _CACHE:
        return None
    value, expires = _CACHE[key]
    if time.monotonic() > expires:
        del _CACHE[key]
        return None
    return value


def cache_set(key: str, value: Any, ttl: int = TTL_SECONDS) -> None:
    _CACHE[key] = (value, time.monotonic() + ttl)


def cache_clear() -> None:
    _CACHE.clear()
