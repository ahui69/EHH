#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory System REST API Endpoints
Provides HTTP interface to unified memory system
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .auth import get_current_user
from .memory import (
    get_memory_system,
    memory_add_conversation,
    memory_search,
    memory_add_fact,
    memory_get_health,
    memory_consolidate_now
)
from .helpers import log_info, log_error


router = APIRouter(prefix="/api/memory", tags=["Memory System"])


# ═══════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════

class ConversationTurnRequest(BaseModel):
    user_message: str = Field(..., min_length=1, max_length=10000)
    assistant_response: str = Field(..., min_length=1, max_length=50000)
    intent: str = Field(default="chat", max_length=50)
    metadata: Optional[Dict[str, Any]] = None


class FactRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    tags: Optional[List[str]] = None
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    max_results: int = Field(default=10, ge=1, le=100)
    layers: Optional[List[str]] = None  # ["L1", "L2", etc.]


class MemoryResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str = ""


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@router.post("/conversation", response_model=MemoryResponse)
async def add_conversation_turn(
    request: ConversationTurnRequest,
    user=Depends(get_current_user)
):
    """
    Add conversation turn to memory system
    
    **Automatically:**
    - Adds to L0 (STM)
    - Creates L1 episode
    - Extracts L2 facts (if important)
    - Updates L4 user profile
    
    **Example:**
    ```json
    {
        "user_message": "Lubię programować w Pythonie",
        "assistant_response": "Rozumiem, Python to świetny język!",
        "intent": "preference",
        "metadata": {"session_id": "abc123"}
    }
    ```
    """
    try:
        result = memory_add_conversation(
            user_id=user["user_id"],
            user_msg=request.user_message,
            assistant_msg=request.assistant_response,
            intent=request.intent,
            metadata=request.metadata
        )
        
        log_info(f"Added conversation turn for user {user['user_id']}", "MEMORY_API")
        
        return MemoryResponse(
            success=True,
            data=result,
            message=f"Conversation turn recorded. Episode: {result['episode_id']}"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fact", response_model=MemoryResponse)
async def add_fact(
    request: FactRequest,
    user=Depends(get_current_user)
):
    """
    Add fact to semantic memory (L2)
    
    **Features:**
    - Automatic deduplication (deterministic ID)
    - Vector embedding generation
    - Confidence-based importance scoring
    
    **Example:**
    ```json
    {
        "content": "FastAPI uses Pydantic for data validation",
        "tags": ["programming", "python", "fastapi"],
        "confidence": 0.95
    }
    ```
    """
    try:
        fact_id = memory_add_fact(
            content=request.content,
            user_id=user["user_id"],
            tags=request.tags,
            confidence=request.confidence
        )
        
        log_info(f"Added fact for user {user['user_id']}: {fact_id}", "MEMORY_API")
        
        return MemoryResponse(
            success=True,
            data={"fact_id": fact_id, "content": request.content},
            message="Fact added to semantic memory"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=MemoryResponse)
async def search_memories(
    request: SearchRequest,
    user=Depends(get_current_user)
):
    """
    Search across all memory layers
    
    **Search Types:**
    - L0 (STM): Recent conversation context
    - L1 (Episodic): Recent events, semantic + temporal
    - L2 (Semantic): Hybrid BM25 + vector similarity
    - L4 (Mental Models): User profile insights
    
    **Ranking:**
    - Semantic similarity (70%)
    - Confidence/importance (20%)
    - Recency (10%)
    
    **Example:**
    ```json
    {
        "query": "Python programming tips",
        "max_results": 20
    }
    ```
    """
    try:
        results = memory_search(
            query=request.query,
            user_id=user["user_id"],
            max_results=request.max_results
        )
        
        log_info(f"Memory search for user {user['user_id']}: {results['total_results']} results", "MEMORY_API")
        
        return MemoryResponse(
            success=True,
            data=results,
            message=f"Found {results['total_results']} relevant memories"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=MemoryResponse)
async def get_memory_health(user=Depends(get_current_user)):
    """
    Get comprehensive memory system health statistics
    
    **Metrics:**
    - L0 (STM): Active conversations, total messages
    - L1 (Episodic): Total episodes, last 24h activity
    - L2 (Semantic): Total facts, average confidence
    - L3 (Procedural): Total procedures, success rates
    - L4 (Mental Models): Total models, confidence
    - Cache: RAM size, Redis availability
    - Overall health score (0-1)
    
    **Health Score Components:**
    - Semantic memory size (at least 100 facts)
    - Semantic confidence (avg > 0.7)
    - Procedural success rate (avg > 0.7)
    - Mental model confidence (avg > 0.6)
    """
    try:
        health = memory_get_health()
        
        return MemoryResponse(
            success=True,
            data=health,
            message=f"Overall health: {health['overall_health']:.2%}"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/consolidate", response_model=MemoryResponse)
async def trigger_consolidation(
    user_id: Optional[str] = Query(None, description="Specific user ID (default: all users)"),
    user=Depends(get_current_user)
):
    """
    Manually trigger memory consolidation
    
    **Process:**
    1. L1 → L2: Consolidate episodes into semantic facts
    2. L2 → L4: Update mental models based on facts
    3. L3: Learn procedural patterns from episodes
    
    **Normally runs automatically every 30 minutes**
    
    **Use Cases:**
    - After importing large dataset
    - Before generating user insights
    - Manual memory optimization
    """
    try:
        # Allow consolidation for own user or all users (admin)
        target_user = user_id if user_id == user["user_id"] or user.get("role") == "admin" else user["user_id"]
        
        stats = memory_consolidate_now(user_id=target_user)
        
        log_info(f"Manual consolidation triggered: {stats}", "MEMORY_API")
        
        return MemoryResponse(
            success=True,
            data=stats,
            message=f"Consolidation complete. Facts created: {stats['facts_created']}, Models updated: {stats['models_updated']}"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/user", response_model=MemoryResponse)
async def get_user_memory_stats(user=Depends(get_current_user)):
    """
    Get memory statistics for current user
    
    **Returns:**
    - Total memories per layer
    - Memory growth over time
    - Top topics/tags
    - Recent activity
    - User profile data
    """
    try:
        mem = get_memory_system()
        user_id = user["user_id"]
        
        # Get stats from each layer
        stm_stats = {
            "messages": len(mem.stm.get_context(user_id))
        }
        
        episodic_stats = {
            "total": len(mem.episodic.get_recent_episodes(user_id, limit=1000)),
            "last_24h": len([
                ep for ep in mem.episodic.get_recent_episodes(user_id, limit=1000)
                if ep.created_at > (datetime.now().timestamp() - 86400)
            ])
        }
        
        semantic_nodes = mem.db.search_nodes(layer="L2", user_id=user_id, limit=1000)
        semantic_stats = {
            "total": len(semantic_nodes),
            "avg_confidence": sum(n.confidence for n in semantic_nodes) / len(semantic_nodes) if semantic_nodes else 0.0,
            "top_tags": [
                {"tag": tag, "count": count}
                for tag, count in sorted(
                    [(tag, sum(1 for n in semantic_nodes for t in n.tags if t == tag))
                     for tag in set(t for n in semantic_nodes for t in n.tags)],
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ]
        }
        
        user_profile = mem.mental_models.get_user_profile(user_id)
        
        return MemoryResponse(
            success=True,
            data={
                "user_id": user_id,
                "stm": stm_stats,
                "episodic": episodic_stats,
                "semantic": semantic_stats,
                "profile": user_profile,
                "timestamp": datetime.now().isoformat()
            },
            message="User memory statistics retrieved successfully"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear", response_model=MemoryResponse)
async def clear_user_memory(
    layers: Optional[List[str]] = Query(None, description="Specific layers to clear (default: all)"),
    user=Depends(get_current_user)
):
    """
    Clear user's memory
    
    **Caution:** This operation cannot be undone!
    
    **Layers:**
    - L0: STM (conversation context)
    - L1: Episodic (recent events)
    - L2: Semantic (facts)
    - L4: Mental models
    
    **Example:** Clear only STM and episodic
    ```
    DELETE /api/memory/clear?layers=L0&layers=L1
    ```
    """
    try:
        mem = get_memory_system()
        user_id = user["user_id"]
        cleared = []
        
        target_layers = layers or ["L0", "L1", "L2", "L4"]
        
        if "L0" in target_layers:
            mem.stm.clear(user_id)
            cleared.append("L0_STM")
        
        if "L1" in target_layers or "L2" in target_layers or "L4" in target_layers:
            with mem.db._conn() as conn:
                if "L1" in target_layers:
                    conn.execute("UPDATE memory_nodes SET deleted=1 WHERE user_id=? AND layer='L1'", (user_id,))
                    cleared.append("L1_Episodic")
                if "L2" in target_layers:
                    conn.execute("UPDATE memory_nodes SET deleted=1 WHERE user_id=? AND layer='L2'", (user_id,))
                    cleared.append("L2_Semantic")
                if "L4" in target_layers:
                    conn.execute("DELETE FROM memory_mental_models WHERE subject=?", (user_id,))
                    cleared.append("L4_Models")
                conn.commit()
        
        # Clear cache
        mem.cache.clear(user_id)
        
        log_info(f"Cleared memory layers for user {user_id}: {cleared}", "MEMORY_API")
        
        return MemoryResponse(
            success=True,
            data={"cleared_layers": cleared},
            message=f"Memory cleared: {', '.join(cleared)}"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


# Export router
__all__ = ["router"]
