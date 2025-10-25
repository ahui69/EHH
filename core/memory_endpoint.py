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
from .cache_invalidation import cleanup_expired_facts, get_cache_ttl, get_fact_age_str
from .personality_presets import get_personality_manager, PERSONALITY_PRESETS
from .conversation_analytics import get_analytics
from .batch_research import get_batch_engine
from .context_awareness import get_context_engine, process_context
from .fact_validation import get_fact_validator, validate_fact, validate_facts


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


class PersonalityRequest(BaseModel):
    personality: str = Field(..., description="Personality preset name")


class BatchResearchRequest(BaseModel):
    queries: List[str] = Field(..., min_items=1, max_items=50, description="List of research queries")
    deduplicate: bool = Field(default=True, description="Remove duplicate queries")


class ContextProcessRequest(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[Dict[str, Any]] = Field(..., description="All conversation messages")
    force_compress: bool = Field(default=False, description="Force compression")


class FactValidationRequest(BaseModel):
    fact: str = Field(..., min_length=1, max_length=5000, description="Fact to validate")
    sources: List[str] = Field(..., min_items=1, description="Source URLs")


class BatchFactValidationRequest(BaseModel):
    facts_with_sources: List[Dict[str, Any]] = Field(..., description="List of {fact, source} dicts")


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


@router.get("/insights", response_model=MemoryResponse)
async def get_memory_insights(user=Depends(get_current_user)):
    """
    GET COMPREHENSIVE MEMORY INSIGHTS DASHBOARD
    
    **Features (FULL LOGIC!):**
    - Layer statistics (L0-L4) with capacity/usage
    - Top accessed facts with age & freshness
    - Consolidation stats (episodes → facts conversion rate)
    - Fuzzy deduplication savings estimate
    - Cache performance metrics
    - Topic distribution analysis
    
    **Example Response:**
    ```json
    {
      "layers": {
        "L0": {"count": 120, "capacity": 500, "usage_pct": 24.0},
        "L2": {"count": 3421, "avg_confidence": 0.87, "top_facts": [...]}
      },
      "consolidation": {
        "total_episodes": 1523,
        "facts_created": 412,
        "conversion_rate": 0.27
      },
      "deduplication": {
        "potential_duplicates": 89,
        "disk_saved_mb": 2.3
      }
    }
    ```
    """
    try:
        mem = get_memory_system()
        user_id = user["user_id"]
        
        # ═══ LAYER STATISTICS ═══
        
        # L0 - Short-Term Memory
        stm_msgs = mem.stm.get_context(user_id)
        l0_stats = {
            "count": len(stm_msgs),
            "capacity": 500,  # From config
            "usage_pct": round((len(stm_msgs) / 500) * 100, 1),
            "oldest_msg_age_sec": (datetime.now().timestamp() - stm_msgs[0].timestamp) if stm_msgs else 0
        }
        
        # L1 - Episodic Memory
        episodes = mem.episodic.get_recent_episodes(user_id, limit=10000)
        l1_stats = {
            "count": len(episodes),
            "last_24h": len([e for e in episodes if e.created_at > (datetime.now().timestamp() - 86400)]),
            "avg_importance": round(sum(e.importance for e in episodes) / len(episodes), 3) if episodes else 0
        }
        
        # L2 - Semantic Facts
        facts = mem.db.search_nodes(layer="L2", user_id=user_id, limit=10000)
        
        # Top 10 facts by access count + age
        top_facts = sorted(
            [
                {
                    "content": f.content[:100] + "..." if len(f.content) > 100 else f.content,
                    "confidence": round(f.confidence, 3),
                    "age": get_fact_age_str(f.created_at),
                    "tags": f.tags[:5],
                    "importance": round(f.importance, 3)
                }
                for f in facts[:100]  # Top 100 by relevance
            ],
            key=lambda x: x["importance"],
            reverse=True
        )[:10]
        
        l2_stats = {
            "count": len(facts),
            "avg_confidence": round(sum(f.confidence for f in facts) / len(facts), 3) if facts else 0,
            "top_facts": top_facts,
            "tags_distribution": dict(sorted(
                [(tag, sum(1 for f in facts for t in f.tags if t == tag))
                 for tag in set(t for f in facts for t in f.tags)],
                key=lambda x: x[1],
                reverse=True
            )[:15])
        }
        
        # L4 - Mental Models
        profile = mem.mental_models.get_user_profile(user_id)
        l4_stats = {
            "total_models": len(profile.get("interests", [])) + len(profile.get("preferences", [])),
            "interests": profile.get("interests", [])[:10],
            "preferences": profile.get("preferences", [])[:10]
        }
        
        # ═══ CONSOLIDATION METRICS ═══
        
        # Query consolidation history
        with mem.db._conn() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM memory_nodes 
                WHERE layer='L2' AND user_id=? AND deleted=0
            """, (user_id,))
            total_facts_created = cursor.fetchone()[0]
        
        consolidation_stats = {
            "total_episodes": len(episodes),
            "facts_created": total_facts_created,
            "conversion_rate": round(total_facts_created / len(episodes), 3) if episodes else 0,
            "last_consolidation": "auto (every 3min)"  # From config
        }
        
        # ═══ FUZZY DEDUPLICATION SAVINGS ═══
        
        # Estimate potential duplicates (90% similarity threshold)
        from difflib import SequenceMatcher
        
        potential_dupes = 0
        sample_facts = facts[:500]  # Sample for performance
        
        for i in range(len(sample_facts)):
            for j in range(i + 1, min(i + 20, len(sample_facts))):  # Check 20 neighbors
                similarity = SequenceMatcher(None, sample_facts[i].content, sample_facts[j].content).ratio()
                if similarity >= 0.90:
                    potential_dupes += 1
        
        # Estimate disk savings (avg fact ~200 bytes)
        disk_saved_mb = round((potential_dupes * 200) / (1024 * 1024), 2)
        
        dedup_stats = {
            "potential_duplicates": potential_dupes,
            "disk_saved_mb": disk_saved_mb,
            "dedup_threshold": 0.90
        }
        
        # ═══ CACHE PERFORMANCE ═══
        
        cache_stats = {
            "type": "RAM + SQLite",
            "ram_cache_mb": round(len(str(mem.cache)) / (1024 * 1024), 2),
            "sqlite_cache_mb": 2048,  # From config
            "mmap_size_mb": 8192  # From config
        }
        
        # ═══ FINAL RESPONSE ═══
        
        return MemoryResponse(
            success=True,
            data={
                "user_id": user_id,
                "layers": {
                    "L0_STM": l0_stats,
                    "L1_Episodic": l1_stats,
                    "L2_Semantic": l2_stats,
                    "L4_MentalModels": l4_stats
                },
                "consolidation": consolidation_stats,
                "deduplication": dedup_stats,
                "cache": cache_stats,
                "timestamp": datetime.now().isoformat()
            },
            message=f"Memory insights for {user_id}: {len(facts)} facts, {len(episodes)} episodes"
        )
    except Exception as e:
        log_error(e, "MEMORY_INSIGHTS")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/cleanup", response_model=MemoryResponse)
async def trigger_cache_cleanup(
    dry_run: bool = Query(False, description="If true, only count expired facts without deleting"),
    user=Depends(get_current_user)
):
    """
    SMART CACHE INVALIDATION - Cleanup expired facts
    
    **TTL Rules (FULL LOGIC!):**
    - News: 1 hour
    - Weather: 30 minutes
    - Stock/Crypto: 5 minutes
    - Sports: 30 minutes
    - Science: 7 days
    - History/Math/Geography: 30 days
    - Programming: 1 day
    - Default: 1 day
    
    **Auto-Detection:**
    Uses NLP keyword matching to categorize facts, then applies category-specific TTL
    
    **Background Task:**
    Runs automatically every hour (configurable)
    
    **Example:**
    ```
    POST /api/memory/cache/cleanup?dry_run=true
    ```
    """
    try:
        mem = get_memory_system()
        
        # Run cleanup
        stats = cleanup_expired_facts(mem, dry_run=dry_run)
        
        log_info(f"Cache cleanup: {stats}", "CACHE_CLEANUP_API")
        
        return MemoryResponse(
            success=True,
            data=stats,
            message=f"{'Would delete' if dry_run else 'Deleted'} {stats['expired_count']} expired facts (checked {stats['total_checked']})"
        )
    except Exception as e:
        log_error(e, "CACHE_CLEANUP_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/personality/list", response_model=MemoryResponse)
async def list_personalities():
    """
    LIST ALL PERSONALITY PRESETS
    
    **Available Presets (FULL LOGIC!):**
    1. **default** - Balanced, professional, helpful
    2. **creative** - Imaginative, expressive, artistic (temp=1.2)
    3. **analytical** - Logical, structured, evidence-based (temp=0.3)
    4. **teacher** - Patient, clear, encouraging (temp=0.6)
    5. **concise** - Brief, direct, actionable (temp=0.5, max_tokens=1000)
    6. **empathetic** - Warm, supportive, validating (temp=0.8)
    7. **scientific** - Rigorous, evidence-based, cautious (temp=0.2)
    8. **socratic** - Inquisitive, thought-provoking, guiding (temp=0.7)
    9. **debug** - Methodical, technical, solution-focused (temp=0.4)
    10. **entrepreneur** - Strategic, pragmatic, opportunity-focused (temp=0.75)
    
    **Each Preset Includes:**
    - Custom system_prompt
    - Optimized temperature
    - Adjusted top_p, frequency_penalty, presence_penalty
    - Custom max_tokens
    - Style notes
    """
    try:
        pm = get_personality_manager()
        presets = pm.list_presets()
        
        return MemoryResponse(
            success=True,
            data={
                "presets": presets,
                "current": pm.current_personality,
                "total_count": len(presets)
            },
            message=f"Found {len(presets)} personality presets"
        )
    except Exception as e:
        log_error(e, "PERSONALITY_LIST")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/personality/current", response_model=MemoryResponse)
async def get_current_personality():
    """
    GET CURRENT PERSONALITY CONFIGURATION
    
    Returns full personality profile with all LLM parameters
    """
    try:
        pm = get_personality_manager()
        profile = pm.get_current_profile()
        params = pm.get_llm_params()
        
        return MemoryResponse(
            success=True,
            data={
                "personality": pm.current_personality,
                "name": profile.name,
                "style_notes": profile.style_notes,
                "llm_params": params
            },
            message=f"Current personality: {profile.name}"
        )
    except Exception as e:
        log_error(e, "PERSONALITY_GET")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/personality/set", response_model=MemoryResponse)
async def set_personality(request: PersonalityRequest):
    """
    SET PERSONALITY PRESET
    
    **Example:**
    ```json
    {"personality": "creative"}
    ```
    
    **Auto-Detection:**
    Can also auto-detect best personality from user message context
    """
    try:
        pm = get_personality_manager()
        
        # Validate preset exists
        if request.personality not in PERSONALITY_PRESETS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown personality '{request.personality}'. Use /personality/list to see available presets."
            )
        
        success = pm.set_personality(request.personality)
        profile = pm.get_current_profile()
        
        log_info(f"Personality switched to '{request.personality}'", "PERSONALITY_SET")
        
        return MemoryResponse(
            success=success,
            data={
                "personality": request.personality,
                "name": profile.name,
                "temperature": profile.temperature,
                "style_notes": profile.style_notes
            },
            message=f"Personality set to: {profile.name}"
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "PERSONALITY_SET")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/stats", response_model=MemoryResponse)
async def get_conversation_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user=Depends(get_current_user)
):
    """
    GET CONVERSATION ANALYTICS (FULL LOGIC!)
    
    **Tracks:**
    - Total messages (user + assistant)
    - Messages by role breakdown
    - Top 10 topics with counts
    - Average message length
    - Total tokens used
    - Average response time
    - Active days count
    - Learning velocity (messages per day)
    
    **Use Cases:**
    - User engagement analysis
    - Topic interest tracking
    - Performance optimization
    - Learning progress monitoring
    
    **Example:**
    ```
    GET /api/memory/analytics/stats?days=30
    ```
    """
    try:
        analytics = get_analytics()
        user_id = user["user_id"]
        
        stats = analytics.get_user_stats(user_id, days=days)
        
        return MemoryResponse(
            success=True,
            data=stats,
            message=f"Analytics for {user_id} over {days} days"
        )
    except Exception as e:
        log_error(e, "ANALYTICS_STATS")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/topics", response_model=MemoryResponse)
async def get_topic_trends(
    limit: int = Query(20, ge=1, le=100, description="Max topics to return"),
    user=Depends(get_current_user)
):
    """
    GET TOPIC TRENDS ANALYSIS
    
    **Returns:**
    - Topic name
    - Message count
    - First seen timestamp
    - Last seen timestamp
    - Recency in days
    
    **Sorted by:** Message count (descending)
    """
    try:
        analytics = get_analytics()
        user_id = user["user_id"]
        
        trends = analytics.get_topic_trends(user_id, limit=limit)
        
        return MemoryResponse(
            success=True,
            data={
                "topics": trends,
                "total_count": len(trends)
            },
            message=f"Found {len(trends)} topic trends for {user_id}"
        )
    except Exception as e:
        log_error(e, "ANALYTICS_TOPICS")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/daily", response_model=MemoryResponse)
async def get_daily_activity(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    user=Depends(get_current_user)
):
    """
    GET DAILY ACTIVITY BREAKDOWN
    
    **Returns for each day:**
    - Date
    - Messages count
    - Topics explored
    - Average message length
    - Total tokens
    
    **Use Cases:**
    - Activity heatmaps
    - Engagement patterns
    - Learning velocity visualization
    """
    try:
        analytics = get_analytics()
        user_id = user["user_id"]
        
        activity = analytics.get_daily_activity(user_id, days=days)
        
        return MemoryResponse(
            success=True,
            data={
                "daily_activity": activity,
                "total_days": len(activity)
            },
            message=f"Daily activity for {user_id} over {days} days"
        )
    except Exception as e:
        log_error(e, "ANALYTICS_DAILY")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/batch", response_model=MemoryResponse)
async def batch_web_research(
    request: BatchResearchRequest,
    user=Depends(get_current_user)
):
    """
    BATCH WEB RESEARCH - Parallel multi-query research (5X FASTER!)
    
    **Features (FULL LOGIC!):**
    - Parallel execution (5 workers by default)
    - Automatic deduplication
    - Timeout handling (30s per query)
    - Progress tracking
    - Speedup metrics
    - Auto-save to L2 semantic memory
    
    **Example:**
    ```json
    {
      "queries": [
        "Python async best practices",
        "FastAPI performance tuning",
        "SQLite optimization tips"
      ],
      "deduplicate": true
    }
    ```
    
    **Response:**
    ```json
    {
      "total_queries": 3,
      "successful": 3,
      "failed": 0,
      "total_facts": 87,
      "batch_elapsed_time": 12.4,
      "avg_query_time": 8.2,
      "speedup_factor": 4.8,
      "results": [...]
    }
    ```
    
    **Use Cases:**
    - Research multiple topics simultaneously
    - Competitive analysis (compare X vs Y vs Z)
    - Multi-aspect learning (definition, examples, best practices)
    - Temporal research (2024, 2023, historical)
    """
    try:
        batch_engine = get_batch_engine()
        mem = get_memory_system()
        
        # Run batch research
        results = batch_engine.research_batch(
            queries=request.queries,
            memory_manager=mem,
            deduplicate=request.deduplicate
        )
        
        log_info(f"Batch research completed: {results['successful']}/{results['total_queries']} queries successful", "BATCH_RESEARCH_API")
        
        return MemoryResponse(
            success=True,
            data=results,
            message=f"Batch research complete: {results['successful']}/{results['total_queries']} successful, {results['total_facts']} facts, {results['speedup_factor']:.1f}x speedup"
        )
    except Exception as e:
        log_error(e, "BATCH_RESEARCH_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/context/process", response_model=MemoryResponse)
async def process_conversation_context(
    request: ContextProcessRequest,
    user=Depends(get_current_user)
):
    """
    CONTEXT AWARENESS ENGINE - Smart context compression
    
    **Features (FULL LOGIC!):**
    - Auto-detect długie rozmowy (>50 messages)
    - Smart trimming (40% token reduction)
    - Rolling summary co 50 messages
    - Context compression with importance scoring
    
    **How it works:**
    1. Detects if conversation is long (>50 msgs)
    2. Creates rolling summaries every 50 messages
    3. Trims context using importance scoring:
       - Recency (newer = more important)
       - Content type (questions, code = important)
       - Length (longer = more substantial)
       - Position (first/last = more important)
    4. Compresses to fit token budget (4000 tokens default)
    5. Returns compressed context + stats
    
    **Example Request:**
    ```json
    {
      "conversation_id": "conv123",
      "messages": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
        ...
      ],
      "force_compress": false
    }
    ```
    
    **Example Response:**
    ```json
    {
      "success": true,
      "data": {
        "conversation_id": "conv123",
        "message_count": 120,
        "is_long_conversation": true,
        "compressed": true,
        "original_count": 120,
        "compressed_count": 72,
        "token_reduction_pct": 40.0,
        "rolling_summary": "Previous discussion covered...",
        "processed_messages": [...]
      }
    }
    ```
    
    **Use Cases:**
    - Long customer support conversations
    - Extended coding sessions
    - Multi-day chat threads
    - Token budget optimization
    """
    try:
        engine = get_context_engine()
        
        # Process context
        processed_messages, stats = engine.process_context(
            conversation_id=request.conversation_id,
            messages=request.messages,
            force_compress=request.force_compress
        )
        
        log_info(f"[CONTEXT_API] Processed conversation {request.conversation_id}: {len(request.messages)} → {len(processed_messages)} messages")
        
        return MemoryResponse(
            success=True,
            data={
                **stats,
                "processed_messages": processed_messages
            },
            message=f"Context processed: {len(request.messages)} → {len(processed_messages)} messages" + 
                    (f", {stats['token_reduction_pct']:.1f}% token reduction" if stats.get('compressed') else "")
        )
    except Exception as e:
        log_error(e, "CONTEXT_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/summary/{conversation_id}", response_model=MemoryResponse)
async def get_conversation_summary(
    conversation_id: str,
    user=Depends(get_current_user)
):
    """
    Get rolling summary for conversation
    
    **Returns:**
    Full summary combining all rolling summaries created for this conversation
    """
    try:
        engine = get_context_engine()
        summary = engine.get_conversation_summary(conversation_id)
        
        if summary is None:
            return MemoryResponse(
                success=True,
                data={"summary": None},
                message="No summary available for this conversation"
            )
        
        return MemoryResponse(
            success=True,
            data={"summary": summary, "conversation_id": conversation_id},
            message="Summary retrieved successfully"
        )
    except Exception as e:
        log_error(e, "CONTEXT_SUMMARY_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/fact", response_model=MemoryResponse)
async def validate_single_fact(
    request: FactValidationRequest,
    user=Depends(get_current_user)
):
    """
    MULTI-SOURCE FACT VALIDATION - Validate single fact
    
    **Features (FULL LOGIC!):**
    - Cross-check across 3+ sources
    - Voting system (2/3 sources must agree)
    - Confidence boost (+0.1 for validated facts)
    - Source reliability weighting
    - Fact provenance tracking
    
    **Source Reliability:**
    - High (1.0): Wikipedia, Britannica, ArXiv, Nature, Science
    - Medium (0.8): Reddit, StackOverflow, GitHub, Medium
    - Low (0.6): Twitter, Facebook, YouTube
    - Default (0.7): Other sources
    
    **Validation Process:**
    1. Normalize fact text (lowercase, trim, remove punctuation)
    2. Compare with facts from all sources (85% similarity = same fact)
    3. Calculate agreement score with reliability weighting
    4. If 67% agreement → validated
    5. Boost confidence by +0.1
    6. Track provenance (source URLs, domains, reliability)
    
    **Example Request:**
    ```json
    {
      "fact": "Paris is the capital of France",
      "sources": [
        "https://wikipedia.org/wiki/Paris",
        "https://britannica.com/place/Paris",
        "https://travel.state.gov/france"
      ]
    }
    ```
    
    **Example Response:**
    ```json
    {
      "success": true,
      "data": {
        "fact": "Paris is the capital of France",
        "is_validated": true,
        "confidence": 0.95,
        "source_count": 3,
        "agreement_score": 0.93,
        "sources": ["wikipedia.org", "britannica.com", "travel.state.gov"],
        "provenance": {
          "validation_method": "multi-source",
          "sources": [
            {"url": "wikipedia.org", "reliability": 1.0, "domain": "wikipedia.org"}
          ],
          "total_sources": 3,
          "agreement_threshold": 0.67
        }
      }
    }
    ```
    
    **Use Cases:**
    - Verify web research facts
    - Reduce hallucinations
    - Build trust in AI responses
    - Fact-checking pipelines
    """
    try:
        validator = get_fact_validator()
        
        # Validate
        result = validator.validate(
            fact=request.fact,
            sources=request.sources
        )
        
        log_info(f"[FACT_VALIDATION_API] Fact validated: {result.is_validated}, confidence: {result.confidence:.2f}")
        
        return MemoryResponse(
            success=True,
            data=result.to_dict(),
            message=f"Fact {'validated' if result.is_validated else 'rejected'}: {result.confidence:.2f} confidence from {len(result.sources)} sources"
        )
    except Exception as e:
        log_error(e, "FACT_VALIDATION_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/batch", response_model=MemoryResponse)
async def validate_facts_batch(
    request: BatchFactValidationRequest,
    user=Depends(get_current_user)
):
    """
    BATCH FACT VALIDATION - Validate multiple facts
    
    **Example Request:**
    ```json
    {
      "facts_with_sources": [
        {"fact": "Water boils at 100°C", "source": "https://wikipedia.org/wiki/Water"},
        {"fact": "Water boils at 100°C", "source": "https://britannica.com/science/water"},
        {"fact": "Earth is flat", "source": "https://example.com/conspiracy"}
      ]
    }
    ```
    
    **Returns:**
    List of validation results with confidence scores and provenance
    """
    try:
        validator = get_fact_validator()
        
        # Convert to tuples
        facts_with_sources = [
            (item["fact"], item["source"]) 
            for item in request.facts_with_sources
        ]
        
        # Validate batch
        results = validator.validate_batch(facts_with_sources)
        
        validated_count = sum(1 for r in results if r.is_validated)
        
        log_info(f"[FACT_VALIDATION_BATCH_API] {validated_count}/{len(results)} facts validated")
        
        return MemoryResponse(
            success=True,
            data={
                "results": [r.to_dict() for r in results],
                "total_facts": len(results),
                "validated_count": validated_count,
                "rejection_count": len(results) - validated_count
            },
            message=f"Batch validation complete: {validated_count}/{len(results)} facts validated"
        )
    except Exception as e:
        log_error(e, "FACT_VALIDATION_BATCH_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate/stats", response_model=MemoryResponse)
async def get_validation_stats(user=Depends(get_current_user)):
    """
    Get fact validation statistics
    
    **Returns:**
    - Total validations performed
    - Validated facts count
    - Rejected facts count
    - Cache size
    - Cache hit rate
    - Validation rate
    """
    try:
        validator = get_fact_validator()
        stats = validator.get_stats()
        
        return MemoryResponse(
            success=True,
            data=stats,
            message=f"Validation stats: {stats['validated_facts']}/{stats['total_validations']} validated ({stats['validation_rate']:.1%})"
        )
    except Exception as e:
        log_error(e, "FACT_VALIDATION_STATS_API")
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


# ═══════════════════════════════════════════════════════════════════
# CONVERSATION HISTORY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@router.get("/conversations", response_model=MemoryResponse)
async def list_conversations(
    user=Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    List all conversations for current user
    
    Returns conversation metadata sorted by last activity
    """
    try:
        user_id = user.get("username", "guest")
        mem = get_memory_system()
        
        # Get episodes (L1) grouped by conversation_id
        with mem.db._conn() as conn:
            rows = conn.execute("""
                SELECT 
                    json_extract(metadata, '$.conversation_id') as conv_id,
                    MIN(created_at) as created_at,
                    MAX(created_at) as updated_at,
                    COUNT(*) as message_count,
                    json_extract(metadata, '$.title') as title
                FROM memory_nodes
                WHERE user_id = ? AND layer = 'L1' AND deleted = 0
                    AND json_extract(metadata, '$.conversation_id') IS NOT NULL
                GROUP BY json_extract(metadata, '$.conversation_id')
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset)).fetchall()
        
        conversations = [
            {
                "id": row[0],
                "created_at": row[1],
                "updated_at": row[2],
                "message_count": row[3],
                "title": row[4] or f"Conversation {row[0][:8]}..."
            }
            for row in rows
        ]
        
        return MemoryResponse(
            success=True,
            data={"conversations": conversations, "total": len(conversations)},
            message=f"Found {len(conversations)} conversations"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=MemoryResponse)
async def get_conversation_messages(
    conversation_id: str,
    user=Depends(get_current_user)
):
    """
    Get all messages from a specific conversation
    
    Returns chronological list of user/assistant messages
    """
    try:
        user_id = user.get("username", "guest")
        mem = get_memory_system()
        
        # Get all episodes for this conversation
        with mem.db._conn() as conn:
            rows = conn.execute("""
                SELECT node_id, content, metadata, created_at
                FROM memory_nodes
                WHERE user_id = ? 
                    AND layer = 'L1' 
                    AND deleted = 0
                    AND json_extract(metadata, '$.conversation_id') = ?
                ORDER BY created_at ASC
            """, (user_id, conversation_id)).fetchall()
        
        messages = []
        for row in rows:
            import json
            metadata = json.loads(row[2]) if row[2] else {}
            
            # Extract user and assistant messages from episode
            if metadata.get("user_message"):
                messages.append({
                    "role": "user",
                    "content": metadata["user_message"],
                    "timestamp": row[3]
                })
            if metadata.get("assistant_message"):
                messages.append({
                    "role": "assistant",
                    "content": metadata["assistant_message"],
                    "timestamp": row[3]
                })
        
        return MemoryResponse(
            success=True,
            data={
                "conversation_id": conversation_id,
                "messages": messages,
                "count": len(messages)
            },
            message=f"Retrieved {len(messages)} messages"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}", response_model=MemoryResponse)
async def delete_conversation(
    conversation_id: str,
    user=Depends(get_current_user)
):
    """
    Delete a specific conversation (soft delete)
    """
    try:
        user_id = user.get("username", "guest")
        mem = get_memory_system()
        
        with mem.db._conn() as conn:
            result = conn.execute("""
                UPDATE memory_nodes 
                SET deleted = 1 
                WHERE user_id = ? 
                    AND layer = 'L1'
                    AND json_extract(metadata, '$.conversation_id') = ?
            """, (user_id, conversation_id))
            conn.commit()
            deleted_count = result.rowcount
        
        return MemoryResponse(
            success=True,
            data={"deleted_messages": deleted_count},
            message=f"Deleted conversation {conversation_id}"
        )
    except Exception as e:
        log_error(e, "MEMORY_API")
        raise HTTPException(status_code=500, detail=str(e))


# Export router
__all__ = ["router"]
