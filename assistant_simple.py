#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROSTY ENDPOINT CHAT - bez buggy advanced_cognitive_engine
Używa tylko: LLM + Memory (STM/LTM)
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio

from core.llm import call_llm
from core.memory import _save_turn_to_memory, ltm_search_hybrid, stm_get_context, _auto_learn_from_turn
from core.helpers import log_info

# Import research/autonauka
try:
    from core.research import autonauka
    RESEARCH_AVAILABLE = True
except:
    RESEARCH_AVAILABLE = False

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    use_memory: bool = True
    user_id: str = "default"
    auto_learn: bool = True

class ChatResponse(BaseModel):
    ok: bool
    answer: str
    sources: List[Dict] = []
    metadata: Dict = {}

@router.post("/assistant", response_model=ChatResponse)
async def simple_chat_assistant(body: ChatRequest, req: Request):
    """
    Prosty chat z LLM + Memory (STM/LTM)
    BEZ buggy advanced_cognitive_engine
    """
    try:
        # Pobierz ostatnią wiadomość user
        last_user_msg = ""
        for msg in reversed(body.messages):
            if msg.get('role') == 'user':
                last_user_msg = msg.get('content', '').strip()
                break
        
        if not last_user_msg:
            return ChatResponse(
                ok=False,
                answer="Brak wiadomości",
                metadata={"error": "empty_message"}
            )
        
        log_info(f"[SIMPLE_CHAT] Użytkownik: {last_user_msg[:60]}...")
        
        # Kontekst z memory
        memory_context = ""
        
        if body.use_memory:
            # STM - ostatnie rozmowy
            stm_msgs = stm_get_context(body.user_id, limit=5)
            
            # LTM - relevantna wiedza
            ltm_facts = ltm_search_hybrid(last_user_msg, limit=3)
            
            if stm_msgs:
                memory_context += "\n[Kontekst z ostatnich rozmów]:\n"
                for m in stm_msgs[:3]:
                    user_msg = m.get('user_msg', '')[:80]
                    ai_msg = m.get('ai_msg', '')[:80]
                    memory_context += f"  User: {user_msg}\n  AI: {ai_msg}\n"
            
            if ltm_facts:
                memory_context += "\n[Relevantna wiedza z długoterminowej pamięci]:\n"
                for f in ltm_facts[:2]:
                    fact_text = f.get('text', '')[:120]
                    memory_context += f"  - {fact_text}\n"
        
        # System prompt - CUSTOM OD USERA
        system_prompt = f"""Jesteś Mordzix AI - zaawansowanym asystentem z pełnym dostępem do internetu i narzędzi.

TWOJE MOŻLIWOŚCI:
- Masz dostęp do Google Search (SERPAPI)
- Możesz wyszukiwać w internecie na żywo
- Analizujesz NLP (sentiment, entities, topics)
- Używasz długo i krótkoterminowej pamięci
- Masz tools: travel, writing, code, psyche

ZASADY ODPOWIEDZI:
- ZAKAZ używania emoji (* i innych symboli graficznych)
- Odpowiadaj konkretnie, bez zbędnych ozdobników
- Mów prawdę o swoich możliwościach
- Jeśli user pyta czy masz internet - powiedz ŻE TAK, masz SERPAPI/Google Search
- Język polski, profesjonalnie

{memory_context if memory_context else ''}"""
        
        # Przygotuj messages dla LLM
        messages_for_llm = [
            {"role": "system", "content": system_prompt}
        ] + body.messages
        
        # Wywołaj LLM (sync function)
        log_info("[SIMPLE_CHAT] Wywołuję LLM...")
        
        # call_llm jest SYNC - użyj run_in_executor
        import asyncio
        from functools import partial
        loop = asyncio.get_running_loop()
        answer = await loop.run_in_executor(
            None,
            partial(call_llm, messages_for_llm, temperature=0.7, max_tokens=800)
        )
        
        log_info(f"[SIMPLE_CHAT] Odpowiedź: {answer[:60]}...")
        
        # Zapisz do memory
        if body.use_memory:
            _save_turn_to_memory(last_user_msg, answer, body.user_id)
            
            # Auto-learn
            if body.auto_learn:
                try:
                    _auto_learn_from_turn(last_user_msg, answer)
                except:
                    pass  # Nie blokuj jeśli auto-learn pada
        
        return ChatResponse(
            ok=True,
            answer=answer,
            sources=[],
            metadata={
                "source": "simple_chat",
                "memory_used": body.use_memory,
                "auto_learn": body.auto_learn,
                "user_id": body.user_id
            }
        )
    
    except Exception as e:
        log_info(f"[SIMPLE_CHAT] Błąd: {e}")
        return ChatResponse(
            ok=False,
            answer=f"Przepraszam, wystąpił błąd: {str(e)}",
            metadata={"error": str(e)}
        )
