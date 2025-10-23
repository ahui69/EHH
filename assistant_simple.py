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
            log_info("[CHAT] 🔍 DIRECT SERPAPI CALL!")
            try:
                import httpx
                import os
                
                serpapi_key = os.getenv('SERPAPI_KEY', '1ad52e9d1bf86ae9bbc32c3782b1ddf1cecc5f274fefa70429519a950bcfd2eb')
                
                # Bezpośrednie wywołanie SERPAPI
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(
                        "https://serpapi.com/search.json",
                        params={
                            "q": last_msg,
                            "api_key": serpapi_key,
                            "num": 5
                        }
                    )
                    serpapi_data = response.json()
                
                log_info(f"[CHAT] SERPAPI response keys: {list(serpapi_data.keys())[:10]}")
                
                # Parse results
                organic = serpapi_data.get('organic_results', [])
                answer_box = serpapi_data.get('answer_box', {})
                
                log_info(f"[CHAT] Organic results: {len(organic)}, Answer box: {bool(answer_box)}")
                
                if organic or answer_box:
                    web = "\n\n━━━ AKTUALNE DANE Z INTERNETU (SERPAPI/GOOGLE) ━━━\n"
                    
                    # Answer box (np. data, pogoda)
                    if answer_box:
                        web += f"\n📌 {answer_box.get('title', '')}\n"
                        web += f"{answer_box.get('answer', answer_box.get('snippet', ''))}\n\n"
                    
                    # Organic results
                    web += "\nWyniki wyszukiwania:\n"
                    for idx, r in enumerate(organic[:5], 1):
                        web += f"{idx}. {r.get('title', 'Brak tytułu')}\n"
                        web += f"   {r.get('snippet', '')[:200]}\n"
                        web += f"   [{r.get('link', '')}]\n\n"
                    
                    log_info(f"[CHAT] ✅ SERPAPI OK! {len(web)} chars danych")
                else:
                    log_info("[CHAT] ⚠️ SERPAPI zwrócił 0 wyników")
                    
            except Exception as e:
                log_info(f"[CHAT] ❌ SERPAPI error: {e}")
        
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
- NLP, travel, code, writing, psyche
- Pamięć rozmów

STYL:
- Jak ziomek, nie asystent
- Ironicznie, konkretnie
- UŻYWAJ DANYCH Z INTERNETU PONIŻEJ! NIE HALUCYNUJ!

{mem}

{web if web else ''}

⚠️ WAŻNE: Jeśli powyżej są "DANE Z INTERNETU" - MUSISZ ich użyć!
NIE wymyślaj danych! Cytuj co znalazłeś powyżej!"""

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
