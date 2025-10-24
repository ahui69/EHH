#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MORDZIX AI - Unified Application
Wersja 5.0.0 - Zunifikowana architektura z pełną automatyzacją
"""

import os
import sys
import time
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

# ═══════════════════════════════════════════════════════════════════
# KONFIGURACJA ŚRODOWISKA
# ═══════════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent.absolute()
os.environ.setdefault("AUTH_TOKEN", "ssjjMijaja6969")
os.environ.setdefault("WORKSPACE", str(BASE_DIR))
os.environ.setdefault("MEM_DB", str(BASE_DIR / "mem.db"))

# Prometheus (opcjonalnie)
try:
    from prometheus_client import Counter, Histogram, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
    registry = CollectorRegistry()
    
    REQUESTS_TOTAL = Counter(
        'mordzix_requests_total',
        'Total requests',
        ['method', 'endpoint', 'status'],
        registry=registry
    )
    
    REQUEST_DURATION = Histogram(
        'mordzix_request_duration_seconds',
        'Request duration',
        ['method', 'endpoint'],
        registry=registry
    )
except ImportError:
    PROMETHEUS_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════
app = FastAPI(
    title="Mordzix AI",
    version="5.0.0",
    description="Zaawansowany system AI z pamięcią, uczeniem i pełną automatyzacją",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus middleware
if PROMETHEUS_AVAILABLE:
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        start_time = time.time()
        endpoint = request.url.path
        method = request.method
        
        try:
            response = await call_next(request)
            
            REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status=str(response.status_code)
            ).inc()
            
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
        except Exception as e:
            raise

# ═══════════════════════════════════════════════════════════════════
# INCLUDE ROUTERS - Wszystkie endpointy
# ═══════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("MORDZIX AI - INICJALIZACJA ENDPOINTÓW")
print("="*70 + "\n")

# 1. ASSISTANT (główny chat z AI)
try:
    import assistant_endpoint
    app.include_router(assistant_endpoint.router)
    print("✓ Assistant endpoint      /api/chat/assistant")
except Exception as e:
    print(f"✗ Assistant endpoint: {e}")

# 2. PSYCHE (stan psychiczny AI)
try:
    import psyche_endpoint
    app.include_router(psyche_endpoint.router)
    print("✓ Psyche endpoint         /api/psyche/*")
except Exception as e:
    print(f"✗ Psyche endpoint: {e}")

# 3. PROGRAMISTA (wykonywanie kodu)
try:
    import programista_endpoint
    app.include_router(programista_endpoint.router)
    print("✓ Programista endpoint    /api/code/*")
except Exception as e:
    print(f"✗ Programista endpoint: {e}")

# 4. FILES (upload, analiza plików)
try:
    import files_endpoint
    app.include_router(files_endpoint.router)
    print("✓ Files endpoint          /api/files/*")
except Exception as e:
    print(f"✗ Files endpoint: {e}")

# 5. TRAVEL (wyszukiwanie podróży)
try:
    import travel_endpoint
    app.include_router(travel_endpoint.router)
    print("✓ Travel endpoint         /api/travel/*")
except Exception as e:
    print(f"✗ Travel endpoint: {e}")

# 6. ADMIN (statystyki, cache)
try:
    import admin_endpoint
    app.include_router(admin_endpoint.router)
    print("✓ Admin endpoint          /api/admin/*")
except Exception as e:
    print(f"✗ Admin endpoint: {e}")

# 7. CAPTCHA (rozwiązywanie captcha)
try:
    import captcha_endpoint
    app.include_router(captcha_endpoint.router, prefix="/api/captcha", tags=["captcha"])
    print("✓ Captcha endpoint        /api/captcha/*")
except Exception as e:
    print(f"✗ Captcha endpoint: {e}")

# 8. PROMETHEUS (metryki)
try:
    import prometheus_endpoint
    app.include_router(prometheus_endpoint.router, prefix="/api/prometheus", tags=["monitoring"])
    print("✓ Prometheus endpoint     /api/prometheus/*")
except Exception as e:
    print(f"✗ Prometheus endpoint: {e}")

# 9. TTS (text-to-speech)
try:
    import tts_endpoint
    app.include_router(tts_endpoint.router)
    print("✓ TTS endpoint            /api/tts/*")
except Exception as e:
    print(f"✗ TTS endpoint: {e}")

# 10. STT (speech-to-text)
try:
    import stt_endpoint
    app.include_router(stt_endpoint.router)
    print("✓ STT endpoint            /api/stt/*")
except Exception as e:
    print(f"✗ STT endpoint: {e}")

# 11. WRITING (generowanie tekstów)
try:
    import writing_endpoint
    app.include_router(writing_endpoint.router)
    print("✓ Writing endpoint        /api/writing/*")
except Exception as e:
    print(f"✗ Writing endpoint: {e}")

# 12. SUGGESTIONS (proaktywne sugestie)
try:
    import suggestions_endpoint
    app.include_router(suggestions_endpoint.router)
    print("✓ Suggestions endpoint    /api/suggestions/*")
except Exception as e:
    print(f"✗ Suggestions endpoint: {e}")

# 13. BATCH (przetwarzanie wsadowe)
try:
    import batch_endpoint
    app.include_router(batch_endpoint.router)
    print("✓ Batch endpoint          /api/batch/*")
except Exception as e:
    print(f"✗ Batch endpoint: {e}")

# 14. RESEARCH (web search - DuckDuckGo, Wikipedia, SERPAPI)
try:
    import research_endpoint
    app.include_router(research_endpoint.router)
    print("✓ Research endpoint       /api/research/*")
except Exception as e:
    print(f"✗ Research endpoint: {e}")

print("\n" + "="*70 + "\n")

# ═══════════════════════════════════════════════════════════════════
# BASIC ROUTES
# ═══════════════════════════════════════════════════════════════════

@app.get("/api")
@app.get("/status")
async def api_status():
    """Status API"""
    return {
        "ok": True,
        "app": "Mordzix AI",
        "version": "5.0.0",
        "features": {
            "auto_stm_to_ltm": True,
            "auto_learning": True,
            "context_injection": True,
            "psyche_system": True,
            "travel_search": True,
            "code_executor": True,
            "tts_stt": True,
            "file_analysis": True
        },
        "endpoints": {
            "chat": "/api/chat/assistant",
            "chat_stream": "/api/chat/assistant/stream",
            "psyche": "/api/psyche/status",
            "travel": "/api/travel/search",
            "code": "/api/code/exec",
            "files": "/api/files/upload",
            "admin": "/api/admin/stats",
            "tts": "/api/tts/speak",
            "stt": "/api/stt/transcribe"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/api/endpoints/list")
async def list_endpoints():
    """Lista wszystkich endpointów API"""
    endpoints = []
    seen = set()
    
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api"):
            methods = sorted([m for m in route.methods if m not in {"HEAD", "OPTIONS"}])
            identifier = (route.path, tuple(methods))
            
            if identifier not in seen:
                endpoints.append({
                    "path": route.path,
                    "methods": methods,
                    "name": route.name,
                    "tags": list(route.tags) if route.tags else [],
                    "summary": route.summary or ""
                })
                seen.add(identifier)
    
    endpoints.sort(key=lambda e: (e["path"], ",".join(e["methods"])))
    return {"ok": True, "count": len(endpoints), "endpoints": endpoints}

# ═══════════════════════════════════════════════════════════════════
# FRONTEND ROUTES
# ═══════════════════════════════════════════════════════════════════

@app.get("/chat_pro_clean.html", response_class=HTMLResponse)
async def serve_chat_pro_clean():
    """Bezpośredni dostęp do chat_pro_clean.html"""
    chat_path = BASE_DIR / "chat_pro_clean.html"
    if chat_path.exists():
        return HTMLResponse(content=chat_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>404</h1><p>chat_pro_clean.html not found</p>", status_code=404)

@app.get("/", response_class=HTMLResponse)
@app.get("/app", response_class=HTMLResponse)
@app.get("/chat", response_class=HTMLResponse)
async def serve_frontend():
    """Główny interfejs czatu"""
    try:
        # Szukaj pliku interfejsu - PRIORYTET: chat_pro_clean.html
        paths = [
            BASE_DIR / "chat_pro_clean.html",  # NAJNOWSZY - minimalistyczny UI
            BASE_DIR / "chat.html",
            BASE_DIR / "frontend.html",
            BASE_DIR / "dist" / "index.html",
            BASE_DIR / "index.html"
        ]
        
        for path in paths:
            if path.exists():
                return HTMLResponse(content=path.read_text(encoding="utf-8"))
        
        # Fallback - prosty interfejs
        return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Mordzix AI</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; background: #0a0a0a; color: #fff; }
        h1 { color: #ff6600; }
        pre { background: #1a1a1a; padding: 15px; border-radius: 5px; border: 1px solid #333; overflow-x: auto; }
        a { color: #ff6600; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .status { color: #00ff00; }
    </style>
</head>
<body>
    <h1>🚀 Mordzix AI - System Aktywny</h1>
    <p class="status">✅ Backend działa poprawnie! Wersja 5.0.0</p>

    <h2>🎯 Dostępne funkcje:</h2>
    <ul>
        <li>✅ Hierarchical Memory (5 poziomów L0-L4)</li>
        <li>✅ Auto-learning (6 źródeł wiedzy)</li>
        <li>✅ Cognitive Engine (11 intent handlers)</li>
        <li>✅ Advanced Psychology</li>
        <li>✅ Self-Reflection (5 głębokości)</li>
        <li>✅ Multi-Agent Orchestra (7 ról)</li>
        <li>✅ Inner Language (128D embeddings)</li>
        <li>✅ Travel Search & Planning</li>
        <li>✅ Code Executor & Programmer</li>
    </ul>
    
    <h2>📡 Test API:</h2>
    <pre>
curl -X POST http://localhost:8080/api/chat/assistant \\
  -H "Authorization: Bearer ssjjMijaja6969" \\
  -H "Content-Type: application/json" \\
  -d '{
    "messages": [{"role": "user", "content": "Cześć!"}],
    "user_id": "test_user",
    "use_memory": true,
    "auto_learn": true
  }'
    </pre>
    
    <p>
        <a href="/docs">📚 API Documentation</a> | 
        <a href="/api/endpoints/list">📋 Lista Endpoints</a> | 
        <a href="/health">💚 Health Check</a>
    </p>
    
    <p style="color: #666; font-size: 12px; margin-top: 50px;">
        ⚠️ Uwaga: Frontend chat_pro_clean.html nie został znaleziony.<br>
        Upewnij się że plik istnieje w katalogu głównym projektu.
    </p>
</body>
</html>
        """)
    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Frontend Error</h1><p>{str(e)}</p>",
            status_code=500
        )

# PWA Assets
@app.get("/sw.js", include_in_schema=False)
async def serve_sw():
    """Service Worker"""
    paths = [BASE_DIR / "dist" / "sw.js", BASE_DIR / "sw.js"]
    for path in paths:
        if path.exists():
            return FileResponse(path, media_type="application/javascript")
    return HTMLResponse(status_code=404, content="sw.js not found")

@app.get("/manifest.webmanifest", include_in_schema=False)
async def serve_manifest():
    """Web App Manifest"""
    paths = [BASE_DIR / "dist" / "manifest.webmanifest", BASE_DIR / "manifest.webmanifest"]
    for path in paths:
        if path.exists():
            return FileResponse(path, media_type="application/manifest+json")
    return HTMLResponse(status_code=404, content="manifest not found")

@app.get("/favicon.ico", include_in_schema=False)
async def serve_favicon():
    """Favicon"""
    paths = [
        BASE_DIR / "dist" / "favicon.ico",
        BASE_DIR / "favicon.ico",
        BASE_DIR / "icons" / "favicon.ico"
    ]
    for path in paths:
        if path.exists():
            return FileResponse(path, media_type="image/x-icon")
    return HTMLResponse(status_code=404)

# Static files (assets, icons)
if (BASE_DIR / "dist" / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(BASE_DIR / "dist" / "assets")), name="assets")

if (BASE_DIR / "icons").exists():
    app.mount("/icons", StaticFiles(directory=str(BASE_DIR / "icons")), name="icons")

# ═══════════════════════════════════════════════════════════════════
# STARTUP & SHUTDOWN
# ═══════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Inicjalizacja przy starcie"""
    print("\n" + "="*70)
    print("MORDZIX AI - STARTED")
    print("="*70)
    print("\n[INFO] Funkcje:")
    print("  ✓ Auto STM→LTM transfer")
    print("  ✓ Auto-learning (Google + scraping)")
    print("  ✓ Context injection (LTM w prompt)")
    print("  ✓ Psyche system (nastrój AI)")
    print("  ✓ Travel (hotele/restauracje/atrakcje)")
    print("  ✓ Code executor (shell/git/docker)")
    print("  ✓ TTS/STT (ElevenLabs + Whisper)")
    print("\n[INFO] Endpoints:")
    print("  [API] Chat:      POST /api/chat/assistant")
    print("  [API] Stream:    POST /api/chat/assistant/stream")
    print("  [API] Psyche:    GET  /api/psyche/status")
    print("  [API] Travel:    GET  /api/travel/search")
    print("  [API] Code:      POST /api/code/exec")
    print("  [API] Files:     POST /api/files/upload")
    print("  [API] TTS:       POST /api/tts/speak")
    print("  [API] STT:       POST /api/stt/transcribe")
    print("\n[INFO] Interfejs:")
    print("  [WEB] Frontend:  http://localhost:8080/")
    print("  [WEB] Docs:      http://localhost:8080/docs")
    print("\n" + "="*70 + "\n")
    
    # Inicjalizacja bazy danych i pamięci
    try:
        from core.memory import _init_db, load_ltm_to_memory
        _init_db()
        load_ltm_to_memory()
        print("[OK] Pamięć LTM załadowana")
    except Exception as e:
        print(f"[WARN] Błąd inicjalizacji pamięci: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup przy wyłączeniu"""
    print("\n[INFO] Shutting down Mordzix AI...")

# ═══════════════════════════════════════════════════════════════════
# MAIN - Uruchomienie serwera
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description='Mordzix AI Server')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port (default: 8080)')
    parser.add_argument('-H', '--host', default="0.0.0.0", help='Host (default: 0.0.0.0)')
    parser.add_argument('--reload', action='store_true', help='Auto-reload on code changes')
    args = parser.parse_args()
    
    print(f"\n[INFO] Starting server on http://{args.host}:{args.port}")
    print(f"[INFO] API Docs: http://localhost:{args.port}/docs")
    print(f"[INFO] Frontend: http://localhost:{args.port}/\n")
    
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
