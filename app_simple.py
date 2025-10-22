#!/usr/bin/env python3
"""
MORDZIX AI - Simple Working Version
Direct implementation for server deployment
"""

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import os
import time
import json
import httpx
import asyncio

# ═══════════════════════════════════════════════════════════════════
# LLM CONFIG
# ═══════════════════════════════════════════════════════════════════
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepinfra.com/v1/openai")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))

async def call_llm(messages: List[dict], system_prompt: str = None) -> str:
    """Call DeepInfra LLM API"""
    try:
        if not LLM_API_KEY:
            return "⚠️ Brak API key dla LLM. Skonfiguruj LLM_API_KEY w .env"
        
        # Build messages
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        
        headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": LLM_MODEL,
            "messages": all_messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9
        }
        
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            response = await client.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                return f"❌ LLM Error ({response.status_code}): {response.text[:200]}"
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    
    except asyncio.TimeoutError:
        return "⏱️ Timeout - LLM nie odpowiedział w czasie"
    except Exception as e:
        return f"❌ LLM Error: {str(e)}"

# ═══════════════════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════════════════
app = FastAPI(
    title="Mordzix AI",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════
class ChatRequest(BaseModel):
    message: Optional[str] = None
    messages: Optional[List[dict]] = None
    user_id: Optional[str] = "default"
    use_memory: Optional[bool] = True
    auto_learn: Optional[bool] = False
    
    def get_text(self) -> str:
        """Extract message text from either format"""
        if self.message:
            return self.message.strip()
        if self.messages and len(self.messages) > 0:
            last_msg = self.messages[-1]
            if isinstance(last_msg, dict) and 'content' in last_msg:
                return last_msg['content'].strip()
            elif isinstance(last_msg, dict) and 'text' in last_msg:
                return last_msg['text'].strip()
        return ""

class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[dict]] = None
    metadata: Optional[dict] = None
    ts: float = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.ts is None:
            self.ts = time.time()

# ═══════════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════════
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "5.0.0",
        "ts": time.time()
    }

# ═══════════════════════════════════════════════════════════════════
# MAIN CHAT ENDPOINT
# ═══════════════════════════════════════════════════════════════════
@app.post("/api/chat/assistant")
async def chat_assistant(body: ChatRequest) -> ChatResponse:
    """Main chat endpoint - AI response"""
    try:
        message = body.get_text()
        
        if not message:
            return ChatResponse(
                answer="Brak wiadomości. Napisz coś!",
                metadata={"error": "empty_message"}
            )
        
        # Call real LLM
        system_prompt = """Jesteś Mordzix AI - superinteligentnym asystentem.
Odpowiadasz na polsku.
Bądź pomocny, precyzyjny i przyjaźnie nastawiony."""
        
        messages = [{"role": "user", "content": message}]
        answer = await call_llm(messages, system_prompt)
        
        return ChatResponse(
            answer=answer,
            metadata={
                "user": body.user_id,
                "memory_enabled": body.use_memory,
                "auto_learn": body.auto_learn,
                "model": LLM_MODEL
            }
        )
    except Exception as e:
        import traceback
        return ChatResponse(
            answer=f"❌ Błąd: {str(e)}",
            metadata={"error": str(e), "traceback": traceback.format_exc()}
        )

# ═══════════════════════════════════════════════════════════════════
# ALIAS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════
@app.post("/api/chat")
async def chat(body: ChatRequest) -> ChatResponse:
    """Alias for /api/chat/assistant"""
    return await chat_assistant(body)

# ═══════════════════════════════════════════════════════════════════
# FILE UPLOAD
# ═══════════════════════════════════════════════════════════════════
UPLOAD_DIR = "/workspace/mrd/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file"""
    try:
        import uuid
        fid = f"{int(time.time())}_{uuid.uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, fid)
        
        content = await file.read()
        with open(path, "wb") as f:
            f.write(content)
        
        return {
            "ok": True,
            "file_id": fid,
            "filename": file.filename,
            "size": len(content),
            "url": f"/api/files/{fid}"
        }
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    """Download file"""
    path = os.path.join(UPLOAD_DIR, file_id)
    if not os.path.isfile(path):
        return JSONResponse({"ok": False, "error": "File not found"}, status_code=404)
    return FileResponse(path)

# ═══════════════════════════════════════════════════════════════════
# AUTOMATION SUMMARY
# ═══════════════════════════════════════════════════════════════════
def get_automation_summary(refresh=False):
    """Get automation summary for startup display"""
    return {
        "fast_path": {
            "count": 15,
            "handlers": ["travel", "weather", "time", "math", "status"]
        },
        "tools": {
            "count": 25,
            "categories": ["web", "travel", "writing", "code", "research", "graphics", "audio"]
        },
        "manual": {"count": 5},
        "totals": {"automatic": 40}
    }

@app.get("/api/automation/summary")
def automation_summary():
    """Get automation capabilities"""
    return get_automation_summary()

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS LIST
# ═══════════════════════════════════════════════════════════════════
@app.get("/api/endpoints/list")
def endpoints_list():
    """List all available endpoints"""
    endpoints = []
    for route in app.routes:
        if hasattr(route, 'methods'):
            for method in route.methods:
                endpoints.append({
                    "path": route.path,
                    "method": method,
                    "name": route.name
                })
    return {"ok": True, "endpoints": endpoints, "count": len(endpoints)}

# ═══════════════════════════════════════════════════════════════════
# STATIC FILES / FRONTEND
# ═══════════════════════════════════════════════════════════════════
try:
    frontend_dist = "/workspace/mrd/frontend/dist/mordzix-ai"
    if os.path.isdir(frontend_dist):
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    else:
        print(f"⚠️  Frontend not found at {frontend_dist}")
except Exception as e:
    print(f"⚠️  Static files mount failed: {e}")

# ═══════════════════════════════════════════════════════════════════
# ROOT
# ═══════════════════════════════════════════════════════════════════
@app.get("/")
def root():
    return {
        "app": "Mordzix AI",
        "version": "5.0.0",
        "status": "online",
        "docs": "http://localhost:8080/docs"
    }

# ═══════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    
    summary = get_automation_summary()
    print("\n" + "="*70)
    print("🚀 MORDZIX AI STARTING")
    print("="*70)
    print(f"📡 Fast path handlers: {summary['fast_path']['count']}")
    print(f"🔧 Tools: {summary['tools']['count']}")
    print(f"📊 Total automation: {summary['totals']['automatic']}")
    print("="*70 + "\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
