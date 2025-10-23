#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin endpoints: cache stats/clear, ratelimit info
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import time

from core.auth import auth_dependency as _auth_dep

router = APIRouter(prefix="/api/admin", tags=["admin"])

_CACHE_STATS = {
    "memory": {
        "ltm_facts_cached": 0,
        "cache_loaded": False,
    }
}

@router.get("/cache/stats")
async def cache_stats(_=Depends(_auth_dep)) -> Dict[str, Any]:
    data = {"ts": time.time(), **_CACHE_STATS}
    try:
        from core.memory import LTM_FACTS_CACHE, LTM_CACHE_LOADED
        data["memory"]["ltm_facts_cached"] = len(LTM_FACTS_CACHE or [])
        data["memory"]["cache_loaded"] = bool(LTM_CACHE_LOADED)
    except Exception:
        pass
    return {"ok": True, "caches": data}

@router.post("/cache/clear")
async def cache_clear(_=Depends(_auth_dep)) -> Dict[str, Any]:
    try:
        from core.memory import LTM_FACTS_CACHE
        LTM_FACTS_CACHE.clear()
    except Exception:
        pass
    return {"ok": True, "cleared": True, "ts": time.time()}

@router.get("/ratelimit/usage/{user_id}")
async def ratelimit_usage(user_id: str, _=Depends(_auth_dep)) -> Dict[str, Any]:
    return {"ok": True, "user_id": user_id, "used": 0, "window": 60}

@router.get("/ratelimit/config")
async def ratelimit_config(_=Depends(_auth_dep)) -> Dict[str, Any]:
    from core.config import RATE_LIMIT_ENABLED, RATE_LIMIT_PER_MINUTE, RATE_LIMIT_WINDOW
    return {
        "ok": True,
        "enabled": RATE_LIMIT_ENABLED,
        "per_minute": RATE_LIMIT_PER_MINUTE,
        "window": RATE_LIMIT_WINDOW,
    }
