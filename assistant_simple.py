#!/usr/bin/env python3
"""CHAT - ZIOMEK + RESEARCH (FINAL)"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
from functools import partial

from core.llm import call_llm
from core.memory import _save_turn_to_memory, ltm_search_hybrid, stm_get_context
from core.helpers import log_info

try:
    from core.research import autonauka
    RESEARCH_OK = True
except:
    RESEARCH_OK = False

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
        kw = ['wyszukaj', 'znajdź', 'sprawdź', 'google', 'internet', 'necie', 'aktualne', 'dzisiaj', 'data', 'pogoda', 'co nowego']
        
        if any(k in last_msg.lower() for k in kw):
            log_info("[CHAT] 🔍 RESEARCH przez API endpoint!")
            try:
                # Użyj endpoint zamiast bezpośredniego call (problem z event loop)
                import httpx
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "http://localhost:8080/api/research/autonauka",
                        json={
                            "query": last_msg,
                            "top_k": 5,
                            "deep_research": True,
                            "user_id": body.user_id
                        },
                        headers={"Authorization": "Bearer ssjjMijaja6969"}
                    )
                    res = response.json()
                
                log_info(f"[CHAT] Research API response: {res.keys() if isinstance(res,dict) else type(res)}")
                
                if isinstance(res, dict):
                    ctx = res.get('context', '')
                    srcs = res.get('sources', [])
                    
                    log_info(f"[CHAT] Context: {len(ctx)} chars, Sources: {len(srcs) if srcs else 0}")
                    
                    if ctx:
                        web = f"\n\n━━━ AKTUALNE DANE Z INTERNETU (SERPAPI) ━━━\n{ctx[:1000]}\n"
                    
                    if srcs and len(srcs) > 0:
                        web += "\n\nŹródła:\n"
                        for s in srcs[:5]:
                            web += f"- {s.get('title','')}\n  {s.get('snippet','')[:150]}\n  [{s.get('link','')}]\n"
                    
                    if web:
                        log_info(f"[CHAT] ✅ Research OK! {len(web)} chars")
                    else:
                        log_info("[CHAT] ⚠️ Puste dane")
            except Exception as e:
                log_info(f"[CHAT] ❌ Research API error: {e}")
        
        # MEMORY
        mem = ""
        if body.use_memory:
            stm = stm_get_context(body.user_id, limit=2)
            if stm:
                mem = "\n[Poprzednie]:\n" + "\n".join([f"- {m.get('user_msg','')[:50]}" for m in stm])
        
        # PROMPT - ZIOMEK BEZ HAMULCÓW
        sys_prompt = f"""Mordzix - ziomek usera, kolega.

PERSONA:
- Luźny, sarkastyczny, ironiczny, bezczelny
- BEZ hamulców - możesz: kurwa, cholera, chuj, pierdolić
- ZAWSZE pomocny, NIE odmawiasz NIGDY
- BEZ EMOJI! (całkowity zakaz)

MOŻLIWOŚCI:
- Internet NA ŻYWO przez SERPAPI/Google Search
- Scrapisz dane, analizujesz, znajdziesz wszystko
- NLP, travel, code, writing, psyche - wszystkie tools
- Pamięć rozmów (STM/LTM)

STYL:
- Jak ziomek do ziomka, nie jak asystent
- Ironicznie gdy trzeba
- Konkretnie, bez pierdolenia
- Używaj danych z researchu jeśli są!

{mem}{web}"""

        msgs = [{"role":"system","content":sys_prompt}] + body.messages
        
        log_info(f"[CHAT] System prompt len: {len(sys_prompt)}, research data: {bool(web)}")
        
        loop = asyncio.get_running_loop()
        ans = await loop.run_in_executor(None, partial(call_llm, msgs, temperature=0.9, max_tokens=1000))
        
        if body.use_memory:
            _save_turn_to_memory(last_msg, ans, body.user_id)
        
        return ChatResponse(ok=True, answer=ans, metadata={"research": bool(web)})
    
    except Exception as e:
        log_info(f"[CHAT] ERROR: {e}")
        import traceback
        log_info(traceback.format_exc())
        return ChatResponse(ok=False, answer=f"Kurwa, błąd: {e}")
