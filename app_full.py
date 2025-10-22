#!/usr/bin/env python3
"""
MORDZIX AI - Full System with LLM Integration
DeepInfra + Memory + Psyche
"""

from fastapi import FastAPI, Request, UploadFile, File
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
import sqlite3
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepinfra.com/v1/openai")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
MEM_DB = os.getenv("MEM_DB", "/workspace/mrd/mem.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/workspace/mrd/uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(MEM_DB) or ".", exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════
class ChatMessage(BaseModel):
    role: str = "user"
    content: str

class ChatRequest(BaseModel):
    message: Optional[str] = None
    messages: Optional[List[ChatMessage]] = None
    user_id: Optional[str] = "default"
    use_memory: Optional[bool] = True
    auto_learn: Optional[bool] = False
    
    def get_text(self) -> str:
        """Extract message text from either format"""
        if self.message:
            return self.message.strip()
        if self.messages and len(self.messages) > 0:
            last_msg = self.messages[-1]
            if isinstance(last_msg, dict):
                return last_msg.get("content", "").strip()
            return last_msg.content.strip()
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
# LLM
# ═══════════════════════════════════════════════════════════════════
async def call_llm(messages: List[dict], system_prompt: str = None) -> str:
    """Call DeepInfra LLM"""
    try:
        if not LLM_API_KEY:
            return "⚠️ Brak API key. Ustaw LLM_API_KEY w .env"
        
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
                error_text = response.text[:300]
                return f"❌ LLM Error ({response.status_code}): {error_text}"
            
            data = response.json()
            answer = data["choices"][0]["message"]["content"].strip()
            return answer
    
    except asyncio.TimeoutError:
        return "⏱️ Timeout - DeepInfra nie odpowiedział"
    except Exception as e:
        return f"❌ Error: {str(e)[:200]}"

# ═══════════════════════════════════════════════════════════════════
# MEMORY
# ═══════════════════════════════════════════════════════════════════
def init_db():
    """Initialize database"""
    try:
        conn = sqlite3.connect(MEM_DB)
        c = conn.cursor()
        
        # Memory table
        c.execute("""CREATE TABLE IF NOT EXISTS memory(
            id TEXT PRIMARY KEY,
            user_id TEXT,
            role TEXT,
            content TEXT,
            ts REAL
        )""")
        
        # Facts table
        c.execute("""CREATE TABLE IF NOT EXISTS facts(
            id TEXT PRIMARY KEY,
            content TEXT,
            confidence REAL,
            created REAL
        )""")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ DB init error: {e}")

def save_to_memory(user_id: str, role: str, content: str):
    """Save message to memory"""
    try:
        import uuid
        conn = sqlite3.connect(MEM_DB)
        c = conn.cursor()
        msg_id = str(uuid.uuid4())
        c.execute(
            "INSERT INTO memory(id, user_id, role, content, ts) VALUES(?, ?, ?, ?, ?)",
            (msg_id, user_id, role, content, time.time())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Memory save error: {e}")

def get_memory_context(user_id: str, limit: int = 10) -> List[dict]:
    """Get recent messages from memory"""
    try:
        conn = sqlite3.connect(MEM_DB)
        c = conn.cursor()
        c.execute(
            "SELECT role, content FROM memory WHERE user_id=? ORDER BY ts DESC LIMIT ?",
            (user_id, limit)
        )
        rows = c.fetchall()
        conn.close()
        
        # Reverse to get chronological order
        messages = [{"role": row[0], "content": row[1]} for row in reversed(rows)]
        return messages
    except Exception as e:
        print(f"⚠️ Memory fetch error: {e}")
        return []

init_db()

# ═══════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════
app = FastAPI(title="Mordzix AI", version="5.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "5.0.0",
        "llm": "DeepInfra (Qwen3)",
        "ts": time.time()
    }

@app.get("/")
def root():
    return {
        "app": "Mordzix AI",
        "version": "5.0.0",
        "status": "online",
        "features": ["chat", "memory", "llm"]
    }

@app.post("/api/chat/assistant")
async def chat_assistant(body: ChatRequest) -> ChatResponse:
    """Main chat with LLM integration"""
    try:
        message = body.get_text()
        user_id = body.user_id or "default"
        
        if not message:
            return ChatResponse(
                answer="Napisz coś!",
                metadata={"error": "empty"}
            )
        
        # Save user message
        if body.use_memory:
            save_to_memory(user_id, "user", message)
        
        # Get context
        system_prompt = "Jesteś Mordzix - inteligentny asystent AI. Odpowiadaj krótko, precyzyjnie i w naturalnym języku polskim."
        context_messages = []
        
        if body.use_memory:
            context_messages = get_memory_context(user_id, limit=5)
        
        # Add current message
        current_messages = context_messages + [{"role": "user", "content": message}]
        
        # Call LLM
        answer = await call_llm(current_messages, system_prompt)
        
        # Save response
        if body.use_memory:
            save_to_memory(user_id, "assistant", answer)
        
        return ChatResponse(
            answer=answer,
            metadata={
                "user": user_id,
                "memory_enabled": body.use_memory,
                "model": LLM_MODEL,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except Exception as e:
        return ChatResponse(
            answer=f"❌ Błąd: {str(e)[:200]}",
            metadata={"error": str(e)}
        )

@app.post("/api/chat")
async def chat(body: ChatRequest) -> ChatResponse:
    """Alias"""
    return await chat_assistant(body)

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
        return JSONResponse({"ok": False, "error": "Not found"}, status_code=404)
    return FileResponse(path)

@app.get("/api/automation/summary")
def automation_summary():
    """Automation capabilities"""
    return {
        "fast_path": {"count": 15},
        "tools": {"count": 25, "categories": ["web", "travel", "writing", "code"]},
        "manual": {"count": 5},
        "totals": {"automatic": 40}
    }

@app.get("/api/endpoints/list")
def endpoints_list():
    """List endpoints"""
    endpoints = []
    for route in app.routes:
        if hasattr(route, 'methods'):
            for method in route.methods:
                endpoints.append({
                    "path": route.path,
                    "method": method,
                    "name": route.name
                })
    return {"ok": True, "endpoints": endpoints}

# ═══════════════════════════════════════════════════════════════════
# STATIC
# ═══════════════════════════════════════════════════════════════════
try:
    frontend_dist = "/workspace/mrd/frontend/dist/mordzix-ai"
    if os.path.isdir(frontend_dist):
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
except Exception as e:
    print(f"⚠️ Frontend mount failed: {e}")

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 MORDZIX AI - FULL SYSTEM")
    print("="*70)
    print(f"📡 LLM: {LLM_MODEL}")
    print(f"🗄️  Memory: {MEM_DB}")
    print(f"💾 Uploads: {UPLOAD_DIR}")
    print("="*70 + "\n")
    
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
