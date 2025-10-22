#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Module - FULL LOGIC from monolit.py
STM/LTM, AdvancedMemoryManager, TimeManager, Database, Facts, Psyche

NO PLACEHOLDERS - FULL WORKING CODE!
"""

import os, sys, time, json, uuid, sqlite3, datetime, math
from typing import Any, Dict, List, Tuple, Optional
from collections import Counter

# Import from other core modules
from .config import (
    AUTH_TOKEN, BASE_DIR, DB_PATH, HTTP_TIMEOUT,
    STM_LIMIT, LTM_IMPORTANCE_THRESHOLD, LTM_CACHE_SIZE,
    CONTEXT_DICTIONARIES
)
from .helpers import (
    log_info, log_warning, log_error,
    normalize_text as _norm, make_id as _id_for, tokenize as _tok,
    tfidf_cosine as _tfidf_cos, sentences_split as _sentences,
    tag_pii as _tag_pii_in_text
)

# Import nowej pamięci hierarchicznej - lazy import aby uniknąć circular import
hierarchical_memory_manager = None
HIERARCHICAL_MEMORY_AVAILABLE = False

def _init_hierarchical_memory():
    """Lazy initialization of hierarchical memory to avoid circular imports"""
    global hierarchical_memory_manager, HIERARCHICAL_MEMORY_AVAILABLE
    if hierarchical_memory_manager is None:
        try:
            from .hierarchical_memory import hierarchical_memory_manager as hmm
            hierarchical_memory_manager = hmm
            HIERARCHICAL_MEMORY_AVAILABLE = True
            log_info("Hierarchical Memory system is available.", "MEMORY")
        except ImportError as e:
            hierarchical_memory_manager = None
            HIERARCHICAL_MEMORY_AVAILABLE = False
            log_warning(f"Hierarchical Memory system not available: {e}", "MEMORY")


# ═══════════════════════════════════════════════════════════════════
# GLOBAL MEMORY STATE
# ═══════════════════════════════════════════════════════════════════

STM_CONTEXT = {}  # {user_id: [messages]}
LTM_FACTS_CACHE = []
LTM_CACHE_LOADED = False
CONTEXT_ANALYZER = {}

# FTS5 availability flag
FTS5_AVAILABLE = True

# Seed facts paths
SEED_CANDIDATES = [
    os.path.join(BASE_DIR, "seed_facts.jsonl"),
    "/workspace/mrd/seed_facts.jsonl",
    "/app/seed_facts.jsonl",
    "seed_facts.jsonl"
]

# ═══════════════════════════════════════════════════════════════════
# ADVANCED MEMORY MANAGER
# ═══════════════════════════════════════════════════════════════════

class AdvancedMemoryManager:
    """Zaawansowany menedżer pamięci z analizą kontekstu"""

    def __init__(self):
        self.stm_limit = 130  # Zwiększony limit STM
        self.ltm_importance_threshold = 0.7  # Próg ważności dla LTM
        self.context_window = 45  # Okno kontekstu dla analizy

    def add_to_stm(self, message: dict, user_id: str = "default"):
        """Dodaj wiadomość do STM z analizą kontekstu"""
        if user_id not in STM_CONTEXT:
            STM_CONTEXT[user_id] = []

        # Analiza kontekstu wiadomości
        context_analysis = self._analyze_context(message)
        message["context_analysis"] = context_analysis
        message["importance_score"] = self._calculate_importance(message, context_analysis)

        STM_CONTEXT[user_id].append(message)

        # Przenieś ważne wiadomości do LTM
        if message["importance_score"] > self.ltm_importance_threshold:
            self._promote_to_ltm(message, user_id)

        # Ogranicz STM do limitu
        if len(STM_CONTEXT[user_id]) > self.stm_limit:
            STM_CONTEXT[user_id] = STM_CONTEXT[user_id][-self.stm_limit:]

    def _analyze_context(self, message: dict) -> dict:
        """Analiza kontekstu wiadomości"""
        content = message.get("content", "").lower()
        context_score = {"technical": 0, "casual": 0, "sports": 0, "business": 0, "creative": 0, "other": 0}

        # Analiza słów kluczowych
        for category, keywords in CONTEXT_DICTIONARIES.items():
            for subcategory, words in keywords.items():
                for word in words:
                    if word.lower() in content:
                        context_score[category] = context_score.get(category, 0) + 1

        # Określ dominujący kontekst
        dominant_context = max(context_score, key=context_score.get)
        return {
            "dominant": dominant_context,
            "scores": context_score,
            "keywords_found": sum(context_score.values())
        }

    def _calculate_importance(self, message: dict, context_analysis: dict) -> float:
        """Oblicz ważność wiadomości dla LTM"""
        base_score = 0.5

        # Premia za słowa kluczowe
        keywords_bonus = min(context_analysis["keywords_found"] * 0.1, 0.3)

        # Premia za długość (ważne informacje są dłuższe)
        content_length = len(message.get("content", ""))
        length_bonus = min(content_length / 1000, 0.2)

        # Premia za kontekst techniczny (ważniejszy)
        context_bonus = 0.1 if context_analysis["dominant"] == "technical" else 0.0

        total_score = base_score + keywords_bonus + length_bonus + context_bonus
        return min(total_score, 1.0)

    def _promote_to_ltm(self, message: dict, user_id: str):
        """Przenieś ważną wiadomość do LTM."""
        try:
            text = (message or {}).get("content", "").strip()
            if not text:
                return
            tags = (message or {}).get("tags") or f"user:{user_id},stm"
            conf = float((message or {}).get("conf") or 0.75)
            # Zapis do LTM (SQLite + ewentualny FTS)
            ltm_add(text, tags, conf)
            log_info(f"Promoted to LTM: {text[:96]}", "MEMORY")
        except Exception as e:
            log_error(e, "PROMOTE_TO_LTM")

    def get_stm_context(self, user_id: str = "default", limit: int = 10) -> list:
        """Pobierz kontekst STM z analizą"""
        if user_id not in STM_CONTEXT:
            return []

        context = STM_CONTEXT[user_id][-limit:]

        # Dodaj metadane kontekstu
        for msg in context:
            if "context_analysis" not in msg:
                msg["context_analysis"] = self._analyze_context(msg)

        return context

    def search_ltm_context(self, query: str, user_id: str = "default", limit: int = 5) -> list:
        """Wyszukaj w LTM (hybryda cache/SQLite/FTS) i zwróć wyniki z metadanymi."""
        try:
            if not query:
                return []
            results = ltm_search_hybrid(query, limit=limit)
            # Normalizacja minimalna
            norm = []
            for r in results or []:
                if isinstance(r, dict):
                    norm.append({
                        "text": r.get("text", ""),
                        "tags": r.get("tags", ""),
                        "score": float(r.get("score", 0.0)),
                        "source": r.get("source", "ltm"),
                    })
                else:
                    # gdy wynik to sam tekst
                    norm.append({"text": str(r), "tags": "", "score": 0.0, "source": "ltm"})
            return norm[:limit]
        except Exception as e:
            log_error(e, "SEARCH_LTM_CONTEXT")
            return []


# Inicjalizacja zaawansowanego menedżera pamięci
memory_manager = AdvancedMemoryManager()


def get_memory_manager() -> AdvancedMemoryManager:
    """
    Zwraca singleton menedżera pamięci (kompatybilność wsteczna)
    
    Returns:
        AdvancedMemoryManager instance
    """
    return memory_manager


# ═══════════════════════════════════════════════════════════════════
# TIME MANAGER
# ═══════════════════════════════════════════════════════════════════

class TimeManager:
    """Zarządzanie czasem i datą dla asystenta"""

    def __init__(self):
        self.timezone = None

    def get_current_time(self) -> dict:
        """Pobierz aktualny czas i datę"""
        now = datetime.datetime.now()

        return {
            "timestamp": now.timestamp(),
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "day_of_week_pl": self._get_polish_day(now),
            "month": now.strftime("%B"),
            "month_pl": self._get_polish_month(now),
            "year": now.year,
            "is_weekend": now.weekday() >= 5,
            "is_morning": 6 <= now.hour < 12,
            "is_afternoon": 12 <= now.hour < 18,
            "is_evening": 18 <= now.hour < 22,
            "is_night": now.hour >= 22 or now.hour < 6
        }

    def _get_polish_day(self, dt: datetime.datetime) -> str:
        """Pobierz nazwę dnia po polsku"""
        days_pl = {
            "Monday": "poniedziałek",
            "Tuesday": "wtorek",
            "Wednesday": "środa",
            "Thursday": "czwartek",
            "Friday": "piątek",
            "Saturday": "sobota",
            "Sunday": "niedziela"
        }
        return days_pl.get(dt.strftime("%A"), dt.strftime("%A"))

    def _get_polish_month(self, dt: datetime.datetime) -> str:
        """Pobierz nazwę miesiąca po polsku"""
        months_pl = {
            "January": "styczeń",
            "February": "luty",
            "March": "marzec",
            "April": "kwiecień",
            "May": "maj",
            "June": "czerwiec",
            "July": "lipiec",
            "August": "sierpień",
            "September": "wrzesień",
            "October": "październik",
            "November": "listopad",
            "December": "grudzień"
        }
        return months_pl.get(dt.strftime("%B"), dt.strftime("%B"))

    def format_time_greeting(self) -> str:
        """Wygeneruj powitanie czasowe"""
        time_info = self.get_current_time()

        if time_info["is_morning"]:
            return "Dzień dobry"
        elif time_info["is_afternoon"]:
            return "Dzień dobry"
        elif time_info["is_evening"]:
            return "Dobry wieczór"
        else:
            return "Dobranoc"

    def format_date_info(self) -> str:
        """Wygeneruj informacje o dacie"""
        time_info = self.get_current_time()
        return f"Dziś jest {time_info['day_of_week_pl']}, {time_info['date']}"


# Inicjalizacja menedżera czasu
time_manager = TimeManager()


# ═══════════════════════════════════════════════════════════════════
# DATABASE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def _db():
    """Get database connection with optimized settings"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA foreign_keys=ON;")  # Włącz constraint'y dla integralności danych
    try:
        # Agresywne optymalizacje pamięci
        conn.execute("PRAGMA cache_size=-500000;")        # ~500MB - zwiększony cache
        conn.execute("PRAGMA mmap_size=1073741824;")      # 1GB - znacznie zwiększony mmap
        conn.execute("PRAGMA journal_size_limit=134217728;")  # 128MB - większy journal
        conn.execute("PRAGMA page_size=8192;")            # Większe strony dla lepszego sekwencyjnego odczytu
        conn.execute("PRAGMA busy_timeout=30000;")        # Dłuższy timeout dla współbieżnych operacji
        conn.execute("PRAGMA auto_vacuum=INCREMENTAL;")   # Inkrementalne vacuum dla stabilnej wydajności
        conn.execute("PRAGMA secure_delete=OFF;")         # Szybsze usuwanie bez nadpisywania
    except Exception as e:
        log_warning(f"Nie można zastosować wszystkich optymalizacji SQLite: {e}", "DB")
    return conn


def _init_db():
    """Initialize all database tables"""
    c = _db()
    cur = c.cursor()
    
    # Memory tables
    cur.execute("""CREATE TABLE IF NOT EXISTS memory(
        id TEXT PRIMARY KEY, user TEXT, role TEXT, content TEXT, ts REAL
    );""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS memory_long(
        id TEXT PRIMARY KEY, user TEXT, summary TEXT, details TEXT, ts REAL
    );""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS meta_memory(
        id TEXT PRIMARY KEY, user TEXT, key TEXT, value TEXT, conf REAL, ts REAL
    );""")
    
    # Facts (LTM) table
    cur.execute("""CREATE TABLE IF NOT EXISTS facts(
        id TEXT PRIMARY KEY, text TEXT, tags TEXT, conf REAL, created REAL, deleted INTEGER DEFAULT 0
    );""")
    
    # FTS5 for facts
    global FTS5_AVAILABLE
    try:
        cur.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(text, tags);""")
    except Exception as e:
        FTS5_AVAILABLE = False
        log_warning(f"FTS5 not available ({e}). Using fallback LIKE search.", "DB")
    
    # Embeddings
    cur.execute("""CREATE TABLE IF NOT EXISTS mem_embed(
        id TEXT PRIMARY KEY, user TEXT, vec TEXT, ts REAL
    );""")
    
    # Documents
    cur.execute("""CREATE TABLE IF NOT EXISTS docs(
        id TEXT PRIMARY KEY, url TEXT, title TEXT, text TEXT, source TEXT, fetched REAL
    );""")
    
    try:
        cur.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(title, text, url UNINDEXED);""")
    except:
        pass
    
    # Cache
    cur.execute("""CREATE TABLE IF NOT EXISTS cache(
        key TEXT PRIMARY KEY, value TEXT, ts REAL
    );""")
    
    # Psyche related tables
    cur.execute("""CREATE TABLE IF NOT EXISTS psy_state(
        id INTEGER PRIMARY KEY CHECK(id=1),
        mood REAL, energy REAL, focus REAL, openness REAL, directness REAL,
        agreeableness REAL, conscientiousness REAL, neuroticism REAL,
        style TEXT, updated REAL
    );""")

    cur.execute("""CREATE TABLE IF NOT EXISTS psy_episode(
        id TEXT PRIMARY KEY, user TEXT, kind TEXT, valence REAL, intensity REAL, tags TEXT, note TEXT, ts REAL
    );""")

    cur.execute("""CREATE TABLE IF NOT EXISTS psy_reflection(
        id TEXT PRIMARY KEY, summary TEXT, delta_json TEXT, ts REAL
    );""")

    # Knowledge base for auctions
    cur.execute("""CREATE TABLE IF NOT EXISTS kb_auction(
        id TEXT PRIMARY KEY, kind TEXT, key TEXT, val TEXT, weight REAL, ts REAL
    );""")
    
    # ═══════════════════════════════════════════════════════════════════
    # INDEXES - Performance boost dla często używanych queries
    # ═══════════════════════════════════════════════════════════════════
    
    # Facts indexes - KRITYCZNE dla wydajności wyszukiwania
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_deleted ON facts(deleted) WHERE deleted=0;")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_created ON facts(created DESC);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_tags ON facts(tags);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_conf ON facts(conf DESC) WHERE deleted=0;")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_text_prefix ON facts(text) WHERE deleted=0;")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_tags_conf ON facts(tags, conf DESC) WHERE deleted=0;")
    
    # Memory indexes - zoptymalizowane pod częste operacje
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memory_user_ts ON memory(user, ts DESC);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memory_role_ts ON memory(role, ts DESC);") 
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memory_user_role_ts ON memory(user, role, ts DESC);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memory_long_user_ts ON memory_long(user, ts DESC);")
    
    # Cache indexes - szybszy dostęp i czyszczenie
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cache_ts ON cache(ts);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cache_key_prefix ON cache(key);")
    
    # Psyche indexes - szybkie filtrowanie emocji i intensywności
    cur.execute("CREATE INDEX IF NOT EXISTS idx_psy_episode_user_ts ON psy_episode(user, ts DESC);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_psy_episode_ts ON psy_episode(ts DESC);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_psy_episode_kind ON psy_episode(kind);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_psy_episode_valence ON psy_episode(valence);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_psy_episode_intensity ON psy_episode(intensity);")
    
    # FTS Optimization - periodyzcne czyszczenie i optymalizacja
    if FTS5_AVAILABLE:
        try:
            cur.execute("INSERT OR REPLACE INTO facts_fts(facts_fts) VALUES('optimize');")
        except:
            pass
    
    log_info("Advanced database indexes created/verified", "DB")
    
    # Initialize psyche state
    cur.execute("INSERT OR IGNORE INTO psy_state VALUES(1,0.0,0.6,0.6,0.55,0.62,0.55,0.63,0.44,'rzeczowy',?)", (time.time(),))
    
    c.commit()
    c.close()


def _preload_seed_facts():
    """Load seed facts from jsonl file at startup"""
    log_info("Sprawdzam seed_facts.jsonl...", "DB")
    
    conn = _db()
    c = conn.cursor()
    facts_count = c.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    conn.close()
    
    if facts_count < 100:
        log_info(f"Znaleziono tylko {facts_count} faktów w bazie. Ładuję seed_facts.jsonl...", "DB")
        
        for path in SEED_CANDIDATES:
            if not os.path.isfile(path):
                continue
                
            loaded = 0
            log_info(f"Ładuję fakty z: {path}", "DB")
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                            txt = obj.get("text") or obj.get("fact")
                            if txt:
                                category = obj.get("category", "")
                                tags = obj.get("tags", [])
                                if isinstance(tags, list):
                                    tags = ",".join(tags)
                                else:
                                    tags = tags or ""
                                    
                                # Dodaj kategorię do tagów
                                if category and category not in tags:
                                    if tags:
                                        tags = f"{tags},fact,{category}"
                                    else:
                                        tags = f"fact,{category}"
                                        
                                ltm_add(txt, tags, float(obj.get("conf", 0.8)))
                                loaded += 1
                        except Exception as e:
                            log_error(e, "SEED_FACT_PARSE")
                
                log_info(f"Załadowano {loaded} faktów z {path}", "DB")
                if loaded > 0:
                    break
            except Exception as e:
                log_error(e, f"SEED_LOAD_{path}")
        
        log_info("Fakty załadowane.", "DB")
    else:
        log_info(f"Znaleziono {facts_count} faktów w bazie. Pomijam ładowanie.", "DB")


# ═══════════════════════════════════════════════════════════════════
# LTM (Long-Term Memory) FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def ltm_add(text: str, tags: str = "", conf: float = 0.7) -> str:
    """Add fact to Long-Term Memory"""
    tid = _id_for(text)
    conn = _db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO facts VALUES(?,?,?,?,?,0)", (tid, text, tags, float(conf), time.time()))
    try:
        c.execute("INSERT INTO facts_fts(text,tags) VALUES(?,?)", (text, tags))
    except Exception:
        pass
    conn.commit()
    conn.close()
    return tid


def ltm_soft_delete(id_or_text: str) -> int:
    """Soft delete fact from LTM"""
    tid = id_or_text if len(id_or_text) == 40 else _id_for(id_or_text)
    conn = _db()
    c = conn.cursor()
    c.execute("UPDATE facts SET deleted=1 WHERE id=?", (tid,))
    conn.commit()
    n = c.rowcount
    conn.close()
    return n


def ltm_delete(id_or_text: str) -> Dict[str, Any]:
    """Delete fact from LTM (soft delete)"""
    n = ltm_soft_delete(id_or_text)
    return {"ok": True, "deleted": n}


def _fts_safe_query(q: str) -> str:
    """Make FTS query safe"""
    q = q.replace('"', ' ').replace("'", ' ').strip()
    return ' '.join(_tok(q)[:20])


def _fts_bm25(query: str, limit: int = 50) -> List[Tuple[str, float]]:
    """FTS5 BM25 search or fallback to LIKE"""
    if not FTS5_AVAILABLE:
        # Fallback: prosta kwerenda LIKE po facts
        toks = [t for t in _tok(query) if t][:5]
        if not toks:
            return []
        like = "%" + "%".join(toks) + "%"
        conn = _db()
        c = conn.cursor()
        try:
            rows = c.execute("SELECT text FROM facts WHERE deleted=0 AND text LIKE ? LIMIT ?", (like, int(limit))).fetchall()
            return [(r["text"], 0.5) for r in rows]
        finally:
            conn.close()
    
    safe = _fts_safe_query(query)
    conn = _db()
    c = conn.cursor()
    out = []
    try:
        rows = c.execute("""SELECT text, bm25(facts_fts) AS bscore
                          FROM facts_fts WHERE facts_fts MATCH ?
                          ORDER BY bscore ASC LIMIT ?""", (safe, int(limit))).fetchall()
        for r in rows:
            bscore = float(r["bscore"] if r["bscore"] is not None else 10.0)
            out.append((r["text"], 1.0 / (1.0 + max(0.0, bscore))))
    finally:
        conn.close()
    return out


def ltm_search_bm25(q: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search LTM using BM25"""
    hits = _fts_bm25(q, limit)
    res = []
    for text, sc in hits:
        res.append({"text": text, "tags": "", "score": float(sc)})
    return res


def ltm_search_hybrid(q: str, limit: int = 30) -> List[Dict[str, Any]]:
    """Hybrid search: RAM cache -> FTS5 BM25 -> LIKE/TFIDF"""
    # 1) RAM cache (najszybsze)
    if LTM_CACHE_LOADED and LTM_FACTS_CACHE:
        return _ltm_search_from_cache(q, limit)

    # 2) FTS5 BM25 jeśli dostępne
    try:
        if FTS5_AVAILABLE:
            bm = ltm_search_bm25(q, limit=limit)
            if bm:
                return bm
    except Exception:
        pass

    # 3) Fallback: LIKE/TF-IDF na tabeli 'facts'
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        rows = c.execute("SELECT id,text,tags,conf,created FROM facts WHERE deleted=0 LIMIT 5000").fetchall()
        conn.close()
        if not rows:
            return []
        docs = [r[1] or "" for r in rows]
        s_tfidf = _tfidf_cos(q, docs)
        pack = [(s_tfidf[i], rows[i]) for i in range(len(rows))]
        pack.sort(key=lambda x: x[0], reverse=True)
        res = []
        for sc, r in pack[:limit]:
            res.append({"id": r[0], "text": r[1], "tags": r[2], "conf": r[3], "created": r[4], "score": float(sc)})
        return res
    except Exception as e:
        log_error(e, "LTM_FALLBACK_SEARCH")
        return []


def _ltm_search_from_cache(q: str, limit: int = 30) -> List[Dict[str, Any]]:
    """Szukaj w LTM cache (RAM) zamiast SQLite - DUŻO SZYBSZE!"""
    if not LTM_FACTS_CACHE:
        return []
    
    query_tokens = _tok(q)
    query_lower = q.lower()
    
    results = []
    
    for fact in LTM_FACTS_CACHE:
        score = 0.0
        
        # 1. Exact match w tagach (boost 3x)
        tags_lower = fact.get('tags', '').lower()
        for token in query_tokens:
            if token in tags_lower:
                score += 3.0
        
        # 2. Exact match w tekście (boost 2x)
        text_lower = fact.get('text', '').lower()
        if query_lower in text_lower:
            score += 2.0
        
        # 3. Token overlap (TF-IDF style)
        fact_tokens = fact.get('tokens', [])
        fact_tokens_set = set(fact_tokens)
        query_tokens_set = set(query_tokens)
        overlap = fact_tokens_set & query_tokens_set
        
        if overlap:
            score += len(overlap) * 0.5
        
        # 4. Boost by confidence
        score *= fact.get('conf', 0.7)
        
        if score > 0:
            results.append({
                'text': fact['text'],
                'tags': fact.get('tags', ''),
                'score': score,
                'conf': fact.get('conf', 0.7)
            })
    
    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]


def load_ltm_to_memory():
    """Load LTM facts into RAM cache for faster search"""
    global LTM_FACTS_CACHE, LTM_CACHE_LOADED
    
    try:
        conn = _db()
        c = conn.cursor()
        rows = c.execute("SELECT text, tags, conf FROM facts WHERE deleted=0 LIMIT ?", (LTM_CACHE_SIZE,)).fetchall()
        conn.close()
        
        LTM_FACTS_CACHE = []
        for r in rows:
            fact = {
                'text': r['text'],
                'tags': r['tags'] or '',
                'conf': r['conf'],
                'tokens': _tok(r['text'])
            }
            LTM_FACTS_CACHE.append(fact)
        
        LTM_CACHE_LOADED = True
        log_info(f"Loaded {len(LTM_FACTS_CACHE)} facts to RAM cache", "LTM")
    except Exception as e:
        log_error(e, "LOAD_LTM_CACHE")


def facts_reindex() -> Dict[str, Any]:
    """Rebuild LTM search indexes"""
    if not FTS5_AVAILABLE:
        return {"ok": False, "error": "fts5_not_available"}
    
    conn = _db()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM facts_fts")
    except Exception:
        pass
    
    rows = c.execute("SELECT text,tags FROM facts WHERE deleted=0 ORDER BY created DESC").fetchall()
    n = 0
    for r in rows:
        try:
            c.execute("INSERT INTO facts_fts(text,tags) VALUES(?,?)", (r["text"], r["tags"]))
            n += 1
        except Exception:
            pass
    
    conn.commit()
    conn.close()
    return {"ok": True, "indexed": n}


def ltm_reindex() -> Dict[str, Any]:
    """Rebuild LTM search indexes"""
    return facts_reindex()


# ═══════════════════════════════════════════════════════════════════
# BLEND SCORES
# ═══════════════════════════════════════════════════════════════════

def _blend_scores(tfidf: List[float], bm25: List[float], emb: List[float],
                  wt=(0.45, 0.30, 0.25), recency: List[float] = None) -> List[float]:
    """
    Łączy różne metryki wyszukiwania z uwzględnieniem recency bias.
    
    Args:
        tfidf: Wyniki TF-IDF dla dokumentów
        bm25: Wyniki BM25 dla dokumentów
        emb: Wyniki podobieństwa embeddingów
        wt: Wagi dla poszczególnych metryk (tfidf, bm25, emb)
        recency: Opcjonalnie współczynniki świeżości dokumentów (0-1)
    """
    n = max(len(tfidf), len(bm25), len(emb))
    
    def get(a, i):
        return a[i] if i < len(a) else 0.0
    
    out = []
    for i in range(n):
        a = get(tfidf, i) ** 1.15
        b = get(bm25, i) ** 1.10
        c = get(emb, i) ** 1.15
        
        # Harmonic mean dla overlapów
        harm = 0.0
        if a > 0.35 and b > 0.35:
            harm += 0.15 * math.sqrt(a * b)
        if b > 0.35 and c > 0.35:
            harm += 0.15 * math.sqrt(b * c)
        if a > 0.7 and c > 0.7:
            harm += 0.10 * math.sqrt(a * c)
        
        # Podstawowy score
        score = wt[0] * a + wt[1] * b + wt[2] * c + harm
        
        # Zastosowanie recency bias jeśli dostępne
        if recency and i < len(recency):
            recency_boost = 1.0 + 0.35 * math.log1p(max(0, recency[i]))
            score *= recency_boost
        
        out.append(score)
    return out


# ═══════════════════════════════════════════════════════════════════
# FACTS EXTRACTION
# ═══════════════════════════════════════════════════════════════════

def _mk_fact(text: str, base_score: float, tags: List[str]) -> Tuple[str, float, List[str]]:
    """Create fact tuple"""
    t = (text or "").strip()
    if not t:
        return ("", 0.0, tags)
    
    # Adjust score based on negation
    import re
    NEGATION_PAT = re.compile(r"\b(nie|nie\s+bardzo|żadn[eyoa])\b", re.I)
    score_delta = -0.08 if NEGATION_PAT.search(t) else 0.04
    score = max(0.55, min(0.97, base_score + score_delta))
    
    return (t, score, sorted(set(tags)))


def _extract_facts_from_turn(u: str, a: str) -> List[Tuple[str, float, List[str]]]:
    """Extract facts from single conversation turn"""
    facts = []
    
    for role, txt in (("user", u or ""), ("assistant", a or "")):
        for s in _sentences(txt):
            s_clean, pii_tags = _tag_pii_in_text(s)
            
            # Check for preferences
            import re
            if re.search(r"\b(lubię|wolę|preferuję|kocham|nienawidzę|nie\s+lubię)\b", s, re.I):
                facts.append(_mk_fact(f"preferencja: {s_clean}", 0.82 if role == "user" else 0.74, ["stm", "preference"] + pii_tags))
                continue
    
    return facts


def _dedupe_facts(facts: List[Tuple[str, float, List[str]]]) -> List[Tuple[str, float, List[str]]]:
    """Deduplicate facts"""
    by = {}
    for t, sc, tg in facts:
        t2 = (t or "").strip()
        if not t2:
            continue
        fid = _id_for(t2)
        if fid in by:
            ot, os, otg = by[fid]
            by[fid] = (ot, max(os, sc), sorted(set((otg or []) + (tg or []))))
        else:
            by[fid] = (t2, sc, sorted(set(tg or [])))
    return list(by.values())


def _extract_facts(messages: List[dict], max_out: int = 120) -> List[Tuple[str, float, List[str]]]:
    """Extract facts from conversation messages"""
    if not messages:
        return []
    
    all_facts = []
    i = 0
    while i < len(messages):
        role_i = messages[i].get("role")
        u = messages[i].get("content", "") if role_i == "user" else ""
        a = ""
        if i + 1 < len(messages) and messages[i + 1].get("role") == "assistant":
            a = messages[i + 1].get("content", "")
            i += 2
        else:
            i += 1
        all_facts.extend(_extract_facts_from_turn(u, a))
    
    all_facts = _dedupe_facts(all_facts)
    all_facts.sort(key=lambda x: x[1], reverse=True)
    return all_facts[:max_out]


# ═══════════════════════════════════════════════════════════════════
# STM (Short-Term Memory) FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def memory_add(user: str, role: str, content: str) -> str:
    """Add message to memory"""
    mid = uuid.uuid4().hex
    conn = _db()
    c = conn.cursor()
    c.execute("INSERT INTO memory VALUES(?,?,?,?,?)", (mid, user, role, content, time.time()))
    conn.commit()
    conn.close()
    return mid


def memory_get(user: str, n: int = 60) -> List[Dict[str, Any]]:
    """Get last N messages for user"""
    conn = _db()
    c = conn.cursor()
    rows = c.execute("SELECT role,content,ts FROM memory WHERE user=? ORDER BY ts DESC LIMIT ?", (user, n)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def memory_summaries(user: str, n: int = 20) -> List[Dict[str, Any]]:
    """Get memory summaries for user"""
    conn = _db()
    c = conn.cursor()
    rows = c.execute("SELECT summary,details,ts FROM memory_long WHERE user=? ORDER BY ts DESC LIMIT ?", (user, n)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def memory_purge(user: str) -> int:
    """Purge all memory for user"""
    conn = _db()
    c = conn.cursor()
    c.execute("DELETE FROM memory WHERE user=?", (user,))
    conn.commit()
    n = c.rowcount
    conn.close()
    return n


def stm_add(role: str, content: str, user: str = "default") -> str:
    """Dodaj wiadomość do pamięci krótkoterminowej"""
    return memory_add(user, role, content)


def stm_get_context(user: str = "default", limit: int = 20) -> List[Dict[str, Any]]:
    """Pobierz ostatnie wiadomości z pamięci krótkoterminowej"""
    msgs = memory_get(user, n=limit)
    # Odwróć kolejność żeby od najstarszych do najnowszych
    return list(reversed(msgs))


def stm_clear(user: str = "default") -> int:
    """Wyczyść pamięć krótkoterminową dla użytkownika"""
    return memory_purge(user)


# ═══════════════════════════════════════════════════════════════════
# PSYCHE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

PL_POS = {"super", "świetnie", "dzięki", "dobrze", "spoko", "okej", "fajnie", "git", "extra"}
PL_NEG = {"kurwa", "chuj", "zajeb", "wkurw", "błąd", "fatalnie", "źle", "nienawidzę", "masakra"}


def psy_get() -> Dict[str, Any]:
    """Get current psyche state"""
    conn = _db()
    c = conn.cursor()
    r = c.execute("SELECT mood,energy,focus,openness,directness,agreeableness,conscientiousness,neuroticism,style,updated FROM psy_state WHERE id=1").fetchone()
    conn.close()
    return dict(r) if r else {"mood": 0.0, "energy": 0.6, "focus": 0.6, "openness": 0.55, "directness": 0.62, "agreeableness": 0.55, "conscientiousness": 0.63, "neuroticism": 0.44, "style": "rzeczowy", "updated": time.time()}


def psy_set(**kw) -> Dict[str, Any]:
    """Set psyche state"""
    s = psy_get()
    for k in ("mood", "energy", "focus", "openness", "directness", "agreeableness", "conscientiousness", "neuroticism"):
        if k in kw and kw[k] is not None:
            s[k] = max(0.0, min(1.0, float(kw[k])))
    if "style" in kw and kw["style"]:
        s["style"] = str(kw["style"])[:64]
    s["updated"] = time.time()
    
    conn = _db()
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO psy_state(id,mood,energy,focus,openness,directness,agreeableness,conscientiousness,neuroticism,style,updated)
                 VALUES(1,?,?,?,?,?,?,?,?,?,?)""",
              (s["mood"], s["energy"], s["focus"], s["openness"], s["directness"], s["agreeableness"], s["conscientiousness"], s["neuroticism"], s["style"], s["updated"]))
    conn.commit()
    conn.close()
    return s


def psy_episode_add(user: str, kind: str, valence: float, intensity: float, tags: str = "", note: str = "") -> str:
    """Add psyche episode"""
    eid = uuid.uuid4().hex
    conn = _db()
    c = conn.cursor()
    c.execute("INSERT INTO psy_episode VALUES(?,?,?,?,?,?,?,?,?)", (eid, user, kind, float(valence), float(intensity), tags or "", note or "", time.time()))
    conn.commit()
    conn.close()
    
    s = psy_get()
    s["mood"] = max(0.0, min(1.0, s["mood"] + 0.08 * valence * intensity))
    s["energy"] = max(0.0, min(1.0, s["energy"] + (0.05 if valence > 0 else -0.03) * intensity))
    s["neuroticism"] = max(0.0, min(1.0, s["neuroticism"] + (-0.04 if valence > 0 else 0.05) * intensity))
    psy_set(**s)
    return eid


def psy_observe_text(user: str, text: str):
    """Observe text for psyche analysis"""
    tl = text.lower()
    pos = sum(1 for w in PL_POS if w in tl)
    neg = sum(1 for w in PL_NEG if w in tl)
    val = 1.0 if pos > neg else (-1.0 if neg > pos else 0.0)
    inten = min(1.0, 0.2 + 0.1 * (pos + neg))
    tags = ",".join(sorted(set(_tok(text))))
    psy_episode_add(user, "msg", val, inten, tags, "auto")


def psy_reflect() -> Dict[str, Any]:
    """Reflect on recent psyche episodes"""
    conn = _db()
    c = conn.cursor()
    rows = c.execute("SELECT valence,intensity,ts FROM psy_episode ORDER BY ts DESC LIMIT 100").fetchall()
    conn.close()
    
    pos = sum(1 for r in rows if r["valence"] > 0)
    neg = sum(1 for r in rows if r["valence"] < 0)
    s = psy_get()
    hour = time.localtime().tm_hour
    delta = {}
    
    if pos > neg:
        delta["openness"] = +0.04
        delta["agreeableness"] = +0.03
    if neg > pos:
        delta["focus"] = +0.04
        delta["directness"] = +0.03
    if 8 <= hour <= 12:
        delta["energy"] = +0.03
    if 0 <= hour <= 6:
        delta["energy"] = -0.04
    
    for k, v in delta.items():
        s[k] = max(0.0, min(1.0, s.get(k, 0.5) + v))
    
    psy_set(**s)
    
    rid = uuid.uuid4().hex
    conn = _db()
    c = conn.cursor()
    c.execute("INSERT INTO psy_reflection VALUES(?,?,?,?)", (rid, f"pos={pos} neg={neg} hour={hour}", json.dumps(delta, ensure_ascii=False), time.time()))
    conn.commit()
    conn.close()
    
    return {"ok": True, "applied": delta, "state": psy_get()}


def psy_tune() -> Dict[str, Any]:
    """Tune LLM parameters based on psyche"""
    from .config import MORDZIX_SYSTEM_PROMPT
    
    s = psy_get()
    temp = 0.72 + 0.25 * (s["openness"] - 0.5) - 0.12 * (s["directness"] - 0.5) - 0.07 * (s["focus"] - 0.5) + 0.05 * (s["agreeableness"] - 0.5) - 0.06 * (s["neuroticism"] - 0.5)
    temp = round(max(0.2, min(1.25, temp)), 2)
    tone = "dynamiczny" if s["energy"] > 0.55 else "zrównoważony"
    if s["directness"] > 0.72:
        tone = "konkretny"
    
    return {
        "temperature": temp, 
        "tone": tone, 
        "style": s.get("style", "rzeczowy"),
        "persona_prompt": MORDZIX_SYSTEM_PROMPT
    }


def psy_tick():
    """Periodic psyche update"""
    now = time.time()
    key = "psy:last_tick"
    conn = _db()
    c = conn.cursor()
    row = c.execute("SELECT value,ts FROM meta_memory WHERE key=?", (key,)).fetchone()
    last = row["ts"] if row else 0
    
    if now - last >= 1800:  # 30 min
        psy_reflect()
        st = psy_get()
        if st["mood"] < 0.2:
            psy_episode_add("system", "auto", +0.6, 0.8, "selfcare", "boost mood")
        c.execute("INSERT OR REPLACE INTO meta_memory(id,user,key,value,conf,ts) VALUES(?,?,?,?,?,?)",
                  (key, "system", key, str(now), 1.0, now))
        conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
# SYSTEM STATS
# ═══════════════════════════════════════════════════════════════════

def system_stats() -> Dict[str, Any]:
    """Get comprehensive system statistics"""
    try:
        import psutil
    except:
        return {"error": "psutil not available"}
    
    stats = {
        "uptime_s": int(time.time()),
        "process": {
            "pid": os.getpid(),
            "cpu_percent": psutil.Process().cpu_percent(interval=0.1),
            "memory_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
        },
        "system": {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_total_gb": round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
            "memory_available_gb": round(psutil.virtual_memory().available / 1024 / 1024 / 1024, 2),
            "memory_percent": psutil.virtual_memory().percent,
        }
    }
    
    # Database stats
    try:
        conn = _db()
        c = conn.cursor()
        
        stats["database"] = {
            "path": DB_PATH,
            "size_mb": round(os.path.getsize(DB_PATH) / 1024 / 1024, 2) if os.path.exists(DB_PATH) else 0,
            "facts_total": c.execute("SELECT COUNT(*) FROM facts").fetchone()[0],
            "facts_active": c.execute("SELECT COUNT(*) FROM facts WHERE deleted=0").fetchone()[0],
            "memory_messages": c.execute("SELECT COUNT(*) FROM memory").fetchone()[0],
            "memory_summaries": c.execute("SELECT COUNT(*) FROM memory_long").fetchone()[0],
            "psyche_episodes": c.execute("SELECT COUNT(*) FROM psy_episode").fetchone()[0],
        }
        
        conn.close()
    except Exception as e:
        stats["database"] = {"error": str(e)}
    
    # Psyche state
    try:
        psyche = psy_get()
        stats["psyche"] = {
            "mood": round(psyche["mood"], 2),
            "energy": round(psyche["energy"], 2),
            "focus": round(psyche["focus"], 2),
            "style": psyche["style"]
        }
    except:
        pass
    
    return stats


# ═══════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════
# CACHE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def cache_get(key: str, ttl: int) -> Optional[dict]:
    """Get cached value"""
    conn=_db(); c=conn.cursor()
    row=c.execute("SELECT value,ts FROM cache WHERE key=?", (key,)).fetchone()
    conn.close()
    if not row: return None
    if time.time()-row["ts"]>ttl: return None
    try: return json.loads(row["value"])
    except: return None


def cache_put(key: str, value: dict):
    """Put value in cache"""
    conn=_db(); c=conn.cursor()
    c.execute("INSERT OR REPLACE INTO cache(key,value,ts) VALUES(?,?,?)",(key,json.dumps(value,ensure_ascii=False),time.time()))
    conn.commit(); conn.close()


# Initialize database on module import
_init_db()
_preload_seed_facts()

# Load LTM cache
load_ltm_to_memory()

log_info("Memory module initialized", "MEMORY")

# ═══════════════════════════════════════════════════════════════════
# TURN SAVING AND AUTOLEARNING
# ═══════════════════════════════════════════════════════════════════

def _save_turn_to_memory(user_msg: str, assistant_msg: str, user_id: str = "default"):
    """Zapisuje turę rozmowy (user + assistant) do STM i potencjalnie do pamięci hierarchicznej."""
    try:
        stm_ids = []
        if user_msg:
            stm_ids.append(stm_add(role="user", content=user_msg, user=user_id))
        if assistant_msg:
            stm_ids.append(stm_add(role="assistant", content=assistant_msg, user=user_id))
        
        log_info(f"Turn saved to STM for user {user_id}", "MEMORY")

        # Integracja z pamięcią hierarchiczną
        if HIERARCHICAL_MEMORY_AVAILABLE and hierarchical_memory_manager:
            _init_hierarchical_memory()  # Ensure initialized
            if hierarchical_memory_manager:
                # Tutaj zakładamy, że intencja i akcje są dostępne z innego miejsca
                # (np. z silnika kognitywnego). Na potrzeby tej funkcji przekażemy wartości domyślne.
                hierarchical_memory_manager.process_conversation_turn(
                    user_id=user_id,
                    user_message=user_msg,
                    assistant_response=assistant_msg,
                    stm_ids=stm_ids,
                    intent="unknown_in_memory_module" # Ta wartość powinna być przekazana z zewnątrz
                )

    except Exception as e:
        log_error(e, "SAVE_TURN")

def _auto_learn_from_turn(user_msg: str, assistant_msg: str):
    """Ekstrahuje fakty z tury rozmowy i zapisuje je do LTM."""
    try:
        facts = _extract_facts_from_turn(user_msg, assistant_msg)
        if not facts:
            return

        added_count = 0
        for text, conf, tags in facts:
            if conf > LTM_IMPORTANCE_THRESHOLD:
                ltm_add(text, tags=",".join(tags), conf=conf)
                added_count += 1
        
        if added_count > 0:
            log_info(f"Auto-learned {added_count} new facts from turn.", "LEARNER")

    except Exception as e:
        log_error(e, "AUTO_LEARN")
