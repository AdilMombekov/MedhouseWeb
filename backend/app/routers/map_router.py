# -*- coding: utf-8 -*-
"""API для карты точек (Google My Maps embed)."""
import os
from fastapi import APIRouter

router = APIRouter(prefix="/map", tags=["map"])

# ID карты из ссылки: .../edit?mid=1EnFUYAd5niHCSLzADwCIPyKZ7ujrJ0U
DEFAULT_MAP_MID = "1EnFUYAd5niHCSLzADwCIPyKZ7ujrJ0U"


@router.get("/embed")
def get_map_embed():
    """Возвращает URL для встраивания карты Google My Maps (Медхаус)."""
    mid = os.environ.get("GOOGLE_MAP_MID", DEFAULT_MAP_MID)
    embed_url = f"https://www.google.com/maps/d/embed?mid={mid}"
    return {"embedUrl": embed_url, "mid": mid}
