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
        kw = ['wyszukaj', 'znajdź', 'sprawdź', 'google', 'internet', 'necie', 'aktualne', 'dzisiaj', 'data', 'pogoda']
        
        if any(k in last_msg.lower() for k in kw) and RESEARCH_OK:
            log_info("[CHAT] 🔍 RESEARCH!")
            try:
                res = await autonauka(q=last_msg, topk=5)
                log_info(f"[CHAT] Res type: {type(res)}, keys: {res.keys() if isinstance(res,dict) else 'N/A'}")
                
                if isinstance(res, dict) and 'context' in res:
                    web = f"\n\n━━━ INTERNET (SERPAPI) ━━━\n{res['context'][:800]}\n"
                    if 'sources' in res:
                        web += "\nŹródła:\n" + "\n".join([f"- {s.get('title','')} [{s.get('link','')}]" for s in (res['sources'] or [])[:3]])
                    log_info(f"[CHAT] ✅ Research OK!")
            except Exception as e:
                log_info(f"[CHAT] ❌ Research: {e}")
        
        # MEMORY
        mem = ""
        if body.use_memory:
            stm = stm_get_context(body.user_id, limit=2)
            if stm:
                mem = "\n[Poprzednie]:\n" + "\n".join([f"- {m.get('user_msg','')[:50]}" for m in stm])
        
        # PROMPT
        sys_prompt = f"""Mordzix - ziomek usera.

PERSONA:
- Luźny, sarkastyczny, ironiczny  
- BEZ hamulców - możesz: kurwa, cholera, chuj
- ZAWSZE pomocny, NIE odmawiasz
- BEZ EMOJI! (zakaz)

MOŻLIWOŚCI:
- Internet NA ŻYWO (SERPAPI, Google Search)
- NLP, travel, code, writing - wszystko
- Pamięć rozmów

STYL:
- Jak ziomek, nie bot
- Konkretnie, bez pierdolenia
{mem}{web}"""

        msgs = [{"role":"system","content":sys_prompt}] + body.messages
        
        loop = asyncio.get_running_loop()
        ans = await loop.run_in_executor(None, partial(call_llm, msgs, temperature=0.9, max_tokens=1000))
        
        if body.use_memory:
            _save_turn_to_memory(last_msg, ans, body.user_id)
        
        return ChatResponse(ok=True, answer=ans, metadata={"research": bool(web)})
    
    except Exception as e:
        log_info(f"[CHAT] ERROR: {e}")
        return ChatResponse(ok=False, answer=f"Błąd: {e}")
