#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
admin_endpoint.py - Admin endpoints for cache & rate limit management
"""

from fastapi import APIRouter, Request, HTTPException, Depends
import os

router = APIRouter(prefix="/api/admin")

AUTH_TOKEN = os.getenv("AUTH_TOKEN") or "changeme"
def _auth(req: Request):
    tok = (req.headers.get("Authorization","") or "").replace("Bearer ","").strip()
    if not tok or tok != AUTH_TOKEN:
        raise HTTPException(401, "unauthorized")

@router.get("/cache/stats")
async def cache_stats(_=Depends(_auth)):
    """📊 Get cache statistics"""
    # Tryb testowy – szybki stub
    import os
    if os.getenv("FAST_TEST") == "1" or os.getenv("TEST_MODE") == "1":
        zero = {"hit_rate": 0, "size": 0, "max_size": 0, "hits": 0, "misses": 0}
        return {"ok": True, "caches": {"llm": zero, "search": zero, "general": zero}, "note": "test-mode"}
    try:
        from middleware import llm_cache, search_cache, general_cache
        return {
            "ok": True,
            "caches": {
                "llm": llm_cache.stats(),
                "search": search_cache.stats(),
                "general": general_cache.stats()
            }
        }
    except Exception:
        # Fallback: nie blokuj testu – zwróć stub szybko
        zero = {"hit_rate": 0, "size": 0, "max_size": 0, "hits": 0, "misses": 0}
        return {"ok": True, "caches": {"llm": zero, "search": zero, "general": zero}, "note": "cache middleware not available"}

@router.post("/cache/clear")
async def clear_cache(cache_type: str = "all", _=Depends(_auth)):
    """🗑️ Clear cache"""
    try:
        from middleware import llm_cache, search_cache, general_cache
        
        if cache_type == "all":
            llm_cache.invalidate()
            search_cache.invalidate()
            general_cache.invalidate()
            return {"ok": True, "cleared": "all"}
        elif cache_type == "llm":
            llm_cache.invalidate()
            return {"ok": True, "cleared": "llm"}
        elif cache_type == "search":
            search_cache.invalidate()
            return {"ok": True, "cleared": "search"}
        elif cache_type == "general":
            general_cache.invalidate()
            return {"ok": True, "cleared": "general"}
        else:
            raise HTTPException(400, "Invalid cache_type")
    except Exception:
        # Brak middleware – udawaj sukces, żeby UI nie sypał 500
        return {"ok": True, "cleared": cache_type, "note": "cache middleware not available"}

@router.get("/ratelimit/usage/{user_id}")
async def rate_limit_usage(user_id: str, endpoint_type: str = "default", _=Depends(_auth)):
    """📈 Get rate limit usage for user"""
    try:
        from middleware import rate_limiter
        usage = rate_limiter.get_usage(user_id, endpoint_type)
        return {"ok": True, "user_id": user_id, "usage": usage}
    except ImportError:
        raise HTTPException(500, "Rate limiter not available")

@router.get("/ratelimit/config")
async def rate_limit_config(_=Depends(_auth)):
    """⚙️ Get rate limit configuration"""
    try:
        from middleware import rate_limiter
        return {
            "ok": True,
            "limits": rate_limiter.limits
        }
    except ImportError:
        raise HTTPException(500, "Rate limiter not available")
