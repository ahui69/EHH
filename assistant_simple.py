#!/usr/bin/env python3
"""CHAT - ZIOMEK + RESEARCH + MEMORY FIXED"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
from functools import partial
import os

from core.llm import call_llm
from core.memory import _save_turn_to_memory, stm_get_context
from core.helpers import log_info

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    use_memory: bool = True
    user_id: str = "default"

class ChatResponse(BaseModel):
    ok: bool
    answer: str
    sources: List[Dict] = []
    metadata: Dict = {}

@router.post("/assistant")
async def chat(body: ChatRequest, req: Request):
    try:
        last_msg = next((m['content'] for m in reversed(body.messages) if m.get('role')=='user'), "")
        if not last_msg:
            return ChatResponse(ok=False, answer="Brak msg")
        
        log_info(f"[CHAT] {last_msg[:80]}")
        
        # RESEARCH
        web = ""
        kw = ['wyszukaj', 'znajdź', 'sprawdź', 'google', 'internet', 'necie', 'aktualne', 
              'dzisiaj', 'wczoraj', 'data', 'pogoda', 'co nowego', 'kto wygrał', 'mecz', 
              'wynik', 'najnowsze', 'teraz', 'live', 'aktualnie']
        
        if any(k in last_msg.lower() for k in kw):
            log_info("[CHAT] 🔍 SERPAPI!")
            try:
                import httpx
                serpapi_key = os.getenv('SERPAPI_KEY', '1ad52e9d1bf86ae9bbc32c3782b1ddf1cecc5f274fefa70429519a950bcfd2eb')
                
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get("https://serpapi.com/search.json", params={"q": last_msg, "api_key": serpapi_key, "num": 5})
                    serpapi_data = response.json()
                
                organic = serpapi_data.get('organic_results', [])
                answer_box = serpapi_data.get('answer_box', {})
                
                if organic or answer_box:
                    web = "\n\n━━━ DANE Z INTERNETU (SERPAPI) ━━━\n"
                    if answer_box:
                        web += f"\n📌 {answer_box.get('title', '')}\n{answer_box.get('answer', answer_box.get('snippet', ''))}\n\n"
                    web += "Wyniki:\n"
                    for idx, r in enumerate(organic[:5], 1):
                        web += f"{idx}. {r.get('title', '')}\n   {r.get('snippet', '')[:200]}\n   [{r.get('link', '')}]\n\n"
                    log_info(f"[CHAT] ✅ SERPAPI: {len(web)} chars")
            except Exception as e:
                log_info(f"[CHAT] ❌ SERPAPI: {e}")
        
        # MEMORY - FIXED!
        mem = ""
        if body.use_memory:
            stm = stm_get_context(body.user_id, limit=5)
            log_info(f"[CHAT] 🧠 STM returned: {len(stm)} messages")
            
            if stm and len(stm) > 0:
                mem = "\n\n━━━ POPRZEDNIE ROZMOWY ━━━\n"
                for msg in stm:
                    role = msg.get('role', '')
                    txt = msg.get('content', '')
                    if role and txt:
                        prefix = "User" if role == "user" else "AI"
                        mem += f"{prefix}: {txt[:150]}\n"
                mem += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                log_info(f"[CHAT] ✅ Memory context: {len(mem)} chars")
        
        # PROMPT - ZIOMEK
        sys_prompt = f"""Mordzix - ziomek usera.

PERSONA:
- Luźny, sarkastyczny, ironiczny
- BEZ hamulców - może: kurwa, cholera, chuj
- ZAWSZE pomocny, NIE odmawiasz

MOŻLIWOŚCI:
- Internet NA ŻYWO (SERPAPI/Google)
- Pamięć rozmów

STYL:
- Jak ziomek, nie bot
- Może emotki (😎🔥💪👍🚀)
- ZAKAZ GWIAZDKA (gwiazdki) - pisz normalnie!
n
KRYTYCZNE - NIE FORMATUJ TEKSTU!
ZAKAZ: **, __, ###, liste, bold, italic
Pisz ZWYKŁYM TEKSTEM!
- UŻYJ DANYCH Z KONTEKSTU POWYŻEJ!

{mem}

{web}"""

        msgs = [{"role":"system","content":sys_prompt}] + body.messages
        
        log_info(f"[CHAT] Prompt: {len(sys_prompt)} chars, mem: {bool(mem)}, web: {bool(web)}")
        
        loop = asyncio.get_running_loop()
        ans = await loop.run_in_executor(None, partial(call_llm, msgs, temperature=0.9, max_tokens=1000))
        
        if body.use_memory:
            _save_turn_to_memory(last_msg, ans, body.user_id)
            log_info(f"[CHAT] ✅ Saved to memory")
        
        return ChatResponse(ok=True, answer=ans, metadata={"research": bool(web), "memory_used": body.use_memory})
    
    except Exception as e:
        log_info(f"[CHAT] ERROR: {e}")
        import traceback
        log_info(traceback.format_exc())
        return ChatResponse(ok=False, answer=f"Kurwa, błąd: {e}")
