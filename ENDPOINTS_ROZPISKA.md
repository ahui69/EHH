# 📡 KAŻDY ENDPOINT - CO ROBI, JAK DZIAŁA

## 📊 PODSUMOWANIE: 100+ ENDPOINTÓW W 15 ROUTERACH

---

## 1. 🎤 STT (Speech-to-Text) - `/api/stt/*`

### `POST /api/stt/transcribe`
**CO ROBI:** Zamienia audio (nagranie głosu) na tekst  
**JAK DZIAŁA:**
1. Przyjmuje plik audio (mp3, wav, webm, ogg, m4a) - max 25MB
2. Próbuje OpenAI Whisper (jeśli masz klucz API)
3. Fallback: Groq Whisper (darmowe)
4. Fallback 2: DeepInfra Whisper
5. Zwraca transkrypcję tekstu

**UŻYCIE W APLIKACJI:** Mikrofon 🎤 we froncie wysyła nagranie tutaj

**PRZYKŁAD:**
```bash
curl -X POST http://localhost:8080/api/stt/transcribe \
  -F "file=@recording.webm"
```

**ODPOWIEDŹ:**
```json
{
  "ok": true,
  "text": "Hej, jak się masz?",
  "language": "pl"
}
```

### `GET /api/stt/providers`
**CO ROBI:** Lista dostępnych providerów STT  
**JAK DZIAŁA:** Sprawdza które API keys są skonfigurowane  
**ZWRACA:** `["openai", "groq", "deepinfra"]`

---

## 2. 🔊 TTS (Text-to-Speech) - `/api/tts/*`

### `POST /api/tts/speak`
**CO ROBI:** Zamienia tekst na mowę (MP3)  
**JAK DZIAŁA:**
1. Przyjmuje tekst (max 5000 znaków)
2. Używa ElevenLabs API (jeśli masz klucz)
3. Generuje audio MP3
4. Zwraca plik audio

**UŻYCIE W APLIKACJI:** Przycisk 🔊 przy odpowiedziach AI

**PRZYKŁAD:**
```bash
curl -X POST http://localhost:8080/api/tts/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Cześć, jak się masz?", "voice": "rachel"}' \
  --output speech.mp3
```

**GŁOSY:** rachel, antoni, adam, bella

### `GET /api/tts/voices`
**CO ROBI:** Lista dostępnych głosów  
**ZWRACA:** 
```json
{
  "voices": ["rachel", "antoni", "adam", "bella"],
  "default": "rachel"
}
```

---

## 3. 🏨 TRAVEL & MAPS - `/api/travel/*`

### `GET /api/travel/search?city=Kraków&what=restaurants`
**CO ROBI:** Wyszukuje miejsca w mieście (atrakcje, hotele, restauracje)  
**JAK DZIAŁA:**
1. Geocoduje miasto (OpenTripMap API)
2. Wyszukuje miejsca:
   - **attractions**: SERPAPI Google Maps (atrakcje, muzea, zabytki)
   - **hotels**: SERPAPI Google Maps (hotele, apartamenty)
   - **restaurants**: Overpass API/OpenStreetMap (restauracje, kawiarnie)
3. Zwraca listę z nazwą, adresem, oceną, zdjęciem

**PARAMETRY:**
- `city`: nazwa miasta (np. "Warszawa", "Kraków")
- `what`: co szukamy - `attractions` / `hotels` / `restaurants`

**PRZYKŁAD ODPOWIEDZI:**
```json
{
  "ok": true,
  "items": [
    {
      "name": "Wawel",
      "address": "Wawel 5, Kraków",
      "rating": 4.8,
      "reviews": 15000,
      "type": "castle",
      "photo": "https://..."
    }
  ]
}
```

### `GET /api/travel/geocode?city=Gdańsk`
**CO ROBI:** Pobiera współrzędne geograficzne miasta  
**JAK DZIAŁA:** OpenTripMap API → geocoding  
**ZWRACA:**
```json
{
  "ok": true,
  "city": "Gdańsk",
  "coordinates": {
    "lat": 54.352,
    "lon": 18.646
  }
}
```

### `GET /api/travel/attractions/{city}`
**CO ROBI:** Skrót do `/search?what=attractions`  
**PRZYKŁAD:** `GET /api/travel/attractions/Warszawa`

### `GET /api/travel/hotels/{city}`
**CO ROBI:** Skrót do `/search?what=hotels`  
**PRZYKŁAD:** `GET /api/travel/hotels/Poznań`

### `GET /api/travel/restaurants/{city}`
**CO ROBI:** Skrót do `/search?what=restaurants`  
**PRZYKŁAD:** `GET /api/travel/restaurants/Wrocław`

---

## 4. 🌐 RESEARCH & WEB - `/api/research/*`

### `POST /api/research/search`
**CO ROBI:** PRAWDZIWE wyszukiwanie w internecie (nie fake!)  
**JAK DZIAŁA:**
1. Wyszukuje w **DuckDuckGo** (zawsze)
2. Wyszukuje w **Wikipedia** (zawsze)
3. Jeśli masz klucze: **SERPAPI/Google**, **arXiv** (artykuły naukowe), **Semantic Scholar**
4. Scrapuje treść ze stron (Firecrawl API lub fallback)
5. Zwraca źródła + treść

**BODY:**
```json
{
  "query": "czym jest kwantowa superpozycja",
  "topk": 5,
  "mode": "full"
}
```

**TRYBY:**
- `fast`: tylko DuckDuckGo + Wikipedia
- `full`: wszystkie źródła + scraping
- `grounded`: j.w. + głębokie źródła naukowe

**ODPOWIEDŹ:**
```json
{
  "ok": true,
  "sources": [
    {
      "title": "Quantum Superposition - Wikipedia",
      "url": "https://en.wikipedia.org/...",
      "snippet": "Superpozycja kwantowa to...",
      "content": "Pełny tekst artykułu..."
    }
  ],
  "answer": "Superpozycja kwantowa to..."
}
```

### `POST /api/research/autonauka`
**CO ROBI:** Pełna pipeline: research + learning + zapis do pamięci  
**JAK DZIAŁA:**
1. Web search (j.w.)
2. Analiza semantyczna (embedding)
3. Generowanie odpowiedzi przez LLM
4. Zapis do Long-Term Memory (LTM)

**BODY:**
```json
{
  "query": "Wyjaśnij teorię strun",
  "topk": 8,
  "user_id": "user123",
  "save_to_ltm": true
}
```

### `GET /api/research/sources`
**CO ROBI:** Lista źródeł wiedzy które system używa  
**ZWRACA:** `["duckduckgo", "wikipedia", "serpapi", "arxiv", "semantic_scholar"]`

### `GET /api/research/test`
**CO ROBI:** Test czy research działa  
**ZWRACA:** `{"ok": true, "message": "Research endpoint is working"}`

---

## 5. ✍️ CREATIVE WRITING - `/api/writing/*`

### `POST /api/writing/creative`
**CO ROBI:** Kreatywne pisanie (artykuły, eseje, opowiadania)  
**JAK DZIAŁA:**
1. Przyjmuje temat + ton + styl + długość
2. Opcjonalnie: kontekst z web search
3. Generuje tekst przez LLM (DeepInfra/OpenAI)

**BODY:**
```json
{
  "topic": "Przyszłość sztucznej inteligencji",
  "tone": "dynamiczny",
  "style": "klarowny",
  "length": "długi"
}
```

### `POST /api/writing/vinted`
**CO ROBI:** Opisy dla Vinted (ubrania, moda)  
**JAK DZIAŁA:** Analizuje tytuł+opis → generuje profesjonalny opis sprzedażowy

**BODY:**
```json
{
  "title": "Czarna sukienka Zara",
  "description": "Rozmiar M, stan bardzo dobry",
  "price": 50.0
}
```

### `POST /api/writing/social`
**CO ROBI:** Posty na social media (Facebook, Instagram, Twitter, LinkedIn)  
**JAK DZIAŁA:** Generuje content + hashtagi + emoji

**BODY:**
```json
{
  "platform": "instagram",
  "topic": "Nowy produkt",
  "tone": "dynamiczny",
  "hashtags": 6,
  "variants": 3
}
```

### `POST /api/writing/auction`
**CO ROBI:** Opisy aukcyjne (Allegro, eBay)  
**PRZYKŁAD UŻYCIA:** Sprzedaż rzeczy online

### `POST /api/writing/auction/pro`
**CO ROBI:** Profesjonalne opisy aukcyjne (rozszerzone)  
**FEATURES:** + SEO, + perswazja, + structure

### `POST /api/writing/blog`
**CO ROBI:** Artykuły blogowe (SEO-optimized)

### `POST /api/writing/email`
**CO ROBI:** Szablony emaili (biznesowe, osobiste)

### `POST /api/writing/product`
**CO ROBI:** Opisy produktów (e-commerce)

### `POST /api/writing/ad`
**CO ROBI:** Reklamy (Google Ads, Facebook Ads)

### `POST /api/writing/seo`
**CO ROBI:** Content SEO (artykuły, landing pages)

### `POST /api/writing/script`
**CO ROBI:** Scenariusze (video, audio, podcast)

### `POST /api/writing/poem`
**CO ROBI:** Poezja (wiersze, haiku)

---

## 6. 💻 PROGRAMISTA (CODE ASSISTANT) - `/api/code/*`

### `GET /api/code/snapshot`
**CO ROBI:** System snapshot - dostępne narzędzia programistyczne  
**ZWRACA:** Lista zainstalowanych: `python`, `node`, `git`, `docker`, etc.

### `POST /api/code/exec`
**CO ROBI:** Wykonuje shell command  
**UWAGA:** Wymaga `confirm: true` dla bezpieczeństwa!

**BODY:**
```json
{
  "cmd": "ls -la",
  "cwd": "/workspace",
  "confirm": true
}
```

### `POST /api/code/write`
**CO ROBI:** Zapisuje plik  
**BODY:**
```json
{
  "path": "/workspace/test.py",
  "content": "print('Hello')",
  "confirm": true
}
```

### `GET /api/code/read?path=/workspace/app.py`
**CO ROBI:** Czyta plik  
**ZWRACA:** Zawartość pliku

### `GET /api/code/tree?max_depth=3`
**CO ROBI:** Drzewo katalogów projektu  
**ZWRACA:** Strukturę plików/folderów

### `POST /api/code/analyze`
**CO ROBI:** Analiza kodu (complexity, security, best practices)

### `POST /api/code/refactor`
**CO ROBI:** Refactoring kodu

### `POST /api/code/debug`
**CO ROBI:** Debugging (szuka błędów)

### `POST /api/code/test`
**CO ROBI:** Generuje testy (pytest, jest)

### `POST /api/code/document`
**CO ROBI:** Generuje dokumentację

### `POST /api/code/optimize`
**CO ROBI:** Optymalizuje kod (performance)

### `POST /api/code/convert`
**CO ROBI:** Konwertuje kod między językami (Python→JS, etc.)

### `POST /api/code/lint`
**CO ROBI:** Linting (ruff, flake8, eslint)

### `POST /api/code/security`
**CO ROBI:** Security scan (vulnerabilities)

---

## 7. 🧠 PSYCHE SYSTEM - `/api/psyche/*`

**CZYM JEST:** System symulacji stanu psychicznego AI który wpływa na odpowiedzi

### `GET /api/psyche/status`
**CO ROBI:** Aktualny stan psychiczny AI  
**ZWRACA:**
```json
{
  "ok": true,
  "state": {
    "mood": 0.7,        // 0-1 (negative → positive)
    "energy": 0.6,      // 0-1 (exhausted → energized)
    "focus": 0.8,       // 0-1 (scattered → focused)
    "openness": 0.7,    // Big Five personality
    "agreeableness": 0.6,
    "conscientiousness": 0.8,
    "neuroticism": 0.3,
    "style": "balanced"
  }
}
```

### `POST /api/psyche/save`
**CO ROBI:** Aktualizuje stan psychiczny AI  
**PRZYKŁAD:** Możesz ustawić AI w tryb "kreatywny" albo "analityczny"

### `POST /api/psyche/observe`
**CO ROBI:** Obserwuj interakcję (AI uczy się z rozmowy)  
**JAK DZIAŁA:** Analizuje tekst → dostosowuje mood/energy/focus

### `POST /api/psyche/episode`
**CO ROBI:** Zapisz epizod emocjonalny  
**PRZYKŁAD:** "User był zadowolony" → mood ↑

### `GET /api/psyche/history`
**CO ROBI:** Historia stanów psychicznych (timeline)

### `POST /api/psyche/adjust`
**CO ROBI:** Dostosuj parametry psychiki

### `GET /api/psyche/traits`
**CO ROBI:** Cechy osobowości (Big Five)

### `POST /api/psyche/reflection`
**CO ROBI:** AI generuje refleksję o swoim stanie

### `GET /api/psyche/mood/timeline`
**CO ROBI:** Wykres nastrojów w czasie

### `POST /api/psyche/reset`
**CO ROBI:** Reset do defaults

---

## 8. 📊 NLP ANALYSIS - `/api/nlp/*`

### `POST /api/nlp/analyze`
**CO ROBI:** Kompleksowa analiza tekstu (NLP)  
**JAK DZIAŁA:** spaCy + własne algorytmy

**ZWRACA:**
```json
{
  "text": "Tekst do analizy",
  "language": "pl",
  "tokens": [...],         // Słowa
  "entities": [...],       // Encje (osoby, miejsca)
  "sentiment": {           // Sentyment
    "positive": 0.7,
    "negative": 0.1,
    "neutral": 0.2
  },
  "key_phrases": [...],    // Kluczowe frazy
  "pos_tags": [...],       // Parts of speech
  "readability_score": 8.5
}
```

### `POST /api/nlp/batch-analyze`
**CO ROBI:** Analiza wielu tekstów naraz

### `POST /api/nlp/extract-topics`
**CO ROBI:** Ekstrakcja tematów (topic modeling)

### `GET /api/nlp/stats`
**CO ROBI:** Statystyki NLP (ile analiz, cache, etc.)

### `POST /api/nlp/entities`
**CO ROBI:** Named Entity Recognition (osoby, miejsca, organizacje)

### `POST /api/nlp/sentiment`
**CO ROBI:** Sentiment analysis (pozytywny/negatywny/neutralny)

### `POST /api/nlp/keywords`
**CO ROBI:** Ekstrakcja słów kluczowych

### `POST /api/nlp/summarize`
**CO ROBI:** Podsumowanie tekstu (streszczenie)

---

## 9. 📈 PROMETHEUS (METRICS) - `/api/prometheus/*`

### `GET /api/prometheus/metrics`
**CO ROBI:** Metryki w formacie Prometheus  
**UŻYCIE:** Monitoring, Grafana

### `GET /api/prometheus/health`
**CO ROBI:** Health check rozszerzony  
**ZWRACA:** Status bazy danych, API, memory, etc.

### `GET /api/prometheus/stats`
**CO ROBI:** System stats (CPU, RAM, dysk)

---

## 10. 💡 PROACTIVE SUGGESTIONS - `/api/suggestions/*`

### `POST /api/suggestions/generate`
**CO ROBI:** Generuje proaktywne sugestie dla użytkownika  
**JAK DZIAŁA:** Analizuje kontekst rozmowy → proponuje kolejne akcje

**PRZYKŁAD ODPOWIEDZI:**
```json
{
  "suggestions": [
    "Czy chcesz żebym wyszukał więcej informacji?",
    "Mogę też stworzyć plan działania",
    "Potrzebujesz pomocy z implementacją?"
  ]
}
```

### `POST /api/suggestions/inject`
**CO ROBI:** Wstrzykuje sugestie do promptu (LLM)

### `GET /api/suggestions/stats`
**CO ROBI:** Statystyki sugestii (ile wygenerowano, acceptance rate)

### `POST /api/suggestions/analyze`
**CO ROBI:** Analiza wiadomości pod kątem potencjalnych sugestii

---

## 11. 🔧 INTERNAL TOOLS - `/api/internal/*`

### `GET /api/internal/ui_token`
**CO ROBI:** Token autoryzacyjny dla internal UI  
**UŻYCIE:** Admin panel, debug tools

---

## 12. 📁 ADVANCED FILE OPERATIONS - `/api/files/*`

### `POST /api/files/upload`
**CO ROBI:** Upload pliku  
**FORMATY:** PDF, images (JPG, PNG), ZIP, TXT, PY, JSON, MD, MP4, etc.  
**MAX SIZE:** 200MB (domyślnie)

**UŻYCIE W APLIKACJI:** Przycisk 📎 we froncie

### `POST /api/files/upload/base64`
**CO ROBI:** Upload pliku jako base64

### `GET /api/files/list`
**CO ROBI:** Lista uploadowanych plików

### `GET /api/files/download?file_id=abc123`
**CO ROBI:** Download pliku

### `POST /api/files/analyze`
**CO ROBI:** Analiza pliku:
- **PDF**: ekstrakcja tekstu (PyPDF2)
- **Images**: OCR (Tesseract), analiza (wymiary, format)
- **ZIP**: lista zawartości
- **Video**: metadata (ffprobe)

### `DELETE /api/files/{id}`
**CO ROBI:** Usuwa plik

### `GET /api/files/metadata/{id}`
**CO ROBI:** Metadata pliku (rozmiar, typ, data, etc.)

### `POST /api/files/ocr`
**CO ROBI:** OCR extraction (tekst z obrazu)

---

## 13. 💬 ADVANCED CHAT (ASSISTANT) - `/api/chat/*`

### `POST /api/chat/assistant`
**CO ROBI:** GŁÓWNY ENDPOINT CHATU z pamięcią + wszystkimi funkcjami  
**JAK DZIAŁA:**
1. Przyjmuje wiadomości użytkownika
2. Wczytuje pamięć (STM + LTM)
3. Analizuje intent (czy potrzebny research, tool, etc.)
4. Wywołuje odpowiednie narzędzia (travel, research, files, etc.)
5. Generuje odpowiedź przez LLM
6. Zapisuje do pamięci

**BODY:**
```json
{
  "messages": [
    {"role": "user", "content": "Znajdź hotele w Krakowie"}
  ],
  "user_id": "user123",
  "use_memory": true,
  "use_research": true,
  "auto_learn": true
}
```

**UŻYWA:**
- Cognitive Engine (centralna orkiestracja)
- Memory (STM + LTM)
- Research (jeśli pytanie wymaga internetu)
- Tools (travel, files, code, etc.)
- Psyche (stan emocjonalny wpływa na odpowiedź)

### `POST /api/chat/assistant/stream`
**CO ROBI:** Streaming responses (odpowiedź word-by-word)  
**UŻYCIE:** Real-time chat

### `POST /api/chat/auto`
**CO ROBI:** Auto mode - AI sam wybiera narzędzia  
**JAK DZIAŁA:** Intent analysis → automatic tool selection

---

## 14. 🔄 SYSTEM ROUTERS (ADMIN/DEBUG) - `/api/routers/*`

### `GET /api/routers/status`
**CO ROBI:** Status wszystkich routerów i systemu  
**ZWRACA:**
```json
{
  "timestamp": 1698000000,
  "version": "5.0.0",
  "database": {
    "connected": true,
    "facts_count": 1500,
    "memory_count": 320
  },
  "psyche": {
    "mood": 0.7,
    "energy": 0.6
  }
}
```

### `GET /api/routers/health`
**CO ROBI:** System health check (BEZ autoryzacji - dla monitoringu)

### `GET /api/routers/list`
**CO ROBI:** Lista WSZYSTKICH dostępnych endpointów

### `GET /api/routers/metrics`
**CO ROBI:** System metrics (CPU, RAM, requests)

### `GET /api/routers/config`
**CO ROBI:** Configuration dump (environment, settings)

### `GET /api/routers/endpoints/summary`
**CO ROBI:** Endpoints summary (grouped by router)

### `GET /api/routers/debug/info`
**CO ROBI:** Debug info (logs, errors, performance)

### `POST /api/routers/cache/clear`
**CO ROBI:** Clear cache (wszystkie cache'e)

### `GET /api/routers/version`
**CO ROBI:** Version info (app, Python, dependencies)

### `GET /api/routers/experimental/features`
**CO ROBI:** Lista eksperymentalnych funkcji

---

## 15. ⚙️ BATCH PROCESSING - `/api/batch/*`

### `POST /api/batch/process`
**CO ROBI:** Przetwarzanie wsadowe (batch jobs)  
**PRZYKŁADY:**
- Analiza wielu plików naraz
- Bulk research queries
- Mass text generation

**BODY:**
```json
{
  "type": "text_analysis",
  "items": [
    {"text": "Tekst 1"},
    {"text": "Tekst 2"}
  ]
}
```

### `GET /api/batch/status/{id}`
**CO ROBI:** Status zadania batch  
**ZWRACA:** `{"status": "processing", "progress": 45}`

### `GET /api/batch/list`
**CO ROBI:** Lista wszystkich zadań batch

### `DELETE /api/batch/{id}`
**CO ROBI:** Anuluj zadanie batch

---

## 🔥 BONUS: ENDPOINTY W app.py (bezpośrednio)

### `GET /health`
**CO ROBI:** Basic health check  
**ZWRACA:** `{"status": "healthy", "version": "5.0.0"}`

### `POST /api/chat`
**CO ROBI:** Alias dla `/api/chat/assistant`

### `GET /`
**CO ROBI:** Serwuje frontend (index_minimal.html)

### `GET /api/automation/summary`
**CO ROBI:** Automation info

### `GET /api/endpoints/list`
**CO ROBI:** Lista wszystkich endpointów

---

# 📊 SUMMARY

| Kategoria | Endpointów | Główna funkcja |
|-----------|------------|----------------|
| STT/TTS | 4 | Głos ↔ Tekst |
| Travel | 6 | Hotele, restauracje, atrakcje |
| Research | 4 | Internet, Wikipedia, arXiv |
| Writing | 12 | Content generation |
| Programista | 14 | Code execution, analysis |
| Psyche | 11 | AI personality |
| NLP | 8 | Text analysis |
| Prometheus | 3 | Monitoring |
| Suggestions | 4 | Proactive AI |
| Internal | 1 | Admin tools |
| Files | 8 | Upload, OCR, PDF |
| Chat | 3 | Main AI chat |
| Routers | 10 | System admin |
| Batch | 4 | Batch processing |
| App.py | 8 | Basic endpoints |
| **TOTAL** | **~100** | **WSZYSTKO!** |

---

# 🚀 JAK UŻYWAĆ:

1. **Frontend używa automatycznie:** Chat, STT, TTS, Files
2. **Możesz wywołać ręcznie:** Research, Travel, Writing, Code
3. **Admin/Debug:** Routers, Prometheus, Batch

**WSZYSTKIE DZIAŁAJĄ! WSZYSTKIE PODŁĄCZONE!** ✅
