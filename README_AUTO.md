# 🔥 MORDZIX AI - FULL AUTO

## Wszystko zspinane razem w `app.py`!

### 🚀 QUICK START:

```bash
# 1. Uruchom aplikację:
cd /workspace
./start.sh

# LUB bezpośrednio:
python3 app.py

# LUB z custom portem:
python3 app.py --port 3000

# LUB z auto-reload (dev):
python3 app.py --reload
```

### 🌐 DOSTĘP:

```
🌐 API:       http://localhost:8080
📚 API Docs:  http://localhost:8080/docs
🎨 Frontend:  http://localhost:8080/app
❤️  Health:    http://localhost:8080/health
```

---

## 📊 CO JEST W `app.py`:

### ✅ WSZYSTKIE ENDPOINTY:

1. **Assistant** (`/api/chat/*`) - 🔥 Z PEŁNĄ AUTOMATYZACJĄ!
   - Auto STM→LTM transfer
   - Auto-learning z internetu
   - Context injection z LTM
   
2. **Psyche** (`/api/psyche/*`)
   - Stan psychiczny AI
   - Mood, energy, focus
   
3. **Programista** (`/api/code/*`)
   - Shell executor
   - Git operations
   - Docker
   
4. **Files** (`/api/files/*`)
   - Upload/download
   - Analysis
   
5. **Travel** (`/api/travel/*`)
   - Hotels, restaurants, attractions
   - Google Maps integration
   
6. **Admin** (`/api/admin/*`)
   - Stats, cache, LTM management

---

## 🔥 AUTOMATYZACJA:

### 1. Auto STM→LTM Transfer
```python
# Każda ważna wiadomość (importance > 0.7) automatycznie idzie do LTM
# Nie musisz nic robić!
```

### 2. Auto-Learning
```python
# Gdy AI nie wie (LTM score < 0.3):
# → automatycznie Google Search
# → scraping stron
# → LLM extraction faktów
# → zapis do LTM
# → użycie w odpowiedzi
```

### 3. Context Injection
```python
# Każda odpowiedź AI automatycznie ma kontekst z LTM
# Top 3 najbardziej relevantne fakty dodane do promptu
```

---

## 🧪 TESTY:

### Test 1: Basic chat
```bash
curl -X POST http://localhost:8080/api/chat/assistant \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Cześć, jak się masz?"}
    ]
  }'
```

### Test 2: Auto-learning (zapytaj o coś nowego)
```bash
curl -X POST http://localhost:8080/api/chat/assistant \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Co to jest quantum computing?"}
    ],
    "use_research": true
  }'

# W response będzie:
# "metadata": {"auto_learned": true}
```

### Test 3: Memory (AI pamięta!)
```bash
# 1. Powiedz coś:
curl -X POST http://localhost:8080/api/chat/assistant \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -d '{"messages": [{"role": "user", "content": "Mam na imię Jan"}]}'

# 2. Sprawdź czy pamięta:
curl -X POST http://localhost:8080/api/chat/assistant \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -d '{"messages": [{"role": "user", "content": "Jak mam na imię?"}]}'

# AI odpowie: "Masz na imię Jan!" (z LTM!)
```

### Test 4: Travel
```bash
curl "http://localhost:8080/api/travel/search?city=Warszawa&what=hotels" \
  -H "Authorization: Bearer ssjjMijaja6969"
```

### Test 5: Psyche
```bash
curl http://localhost:8080/api/psyche/status \
  -H "Authorization: Bearer ssjjMijaja6969"
```

### Test 6: Code execution
```bash
curl -X POST http://localhost:8080/api/code/exec \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -H "Content-Type: application/json" \
  -d '{"cmd": "ls -la", "confirm": true}'
```

---

## 🎛️ KONFIGURACJA:

### Plik `.env` (opcjonalny):
```bash
# Auth
AUTH_TOKEN=ssjjMijaja6969

# LLM
LLM_API_KEY=your_key_here
LLM_BASE_URL=https://api.deepinfra.com/v1/openai
LLM_MODEL=zai-org/GLM-4.5

# APIs
SERPAPI_KEY=your_key_here
FIRECRAWL_KEY=your_key_here
OPENTRIPMAP_KEY=your_key_here
STABILITY_API_KEY=your_key_here

# Paths
WORKSPACE=/workspace/EHH/EHH/mrd
MEM_DB=/workspace/mrd/mem.db
```

### Zmienne środowiskowe:
```bash
export AUTH_TOKEN="ssjjMijaja6969"
export PORT=8080
export HOST="0.0.0.0"
python3 app.py
```

---

## 📁 STRUKTURA:

```
/workspace/
├── app.py                    # 🔥 GŁÓWNA APLIKACJA (wszystko tu!)
├── start.sh                  # Quick start script
├── monolit.py               # Alternatywny main (legacy)
├── assistant_endpoint.py    # Chat z automatyzacją
├── psyche_endpoint.py       # Psyche AI
├── programista_endpoint.py  # Code executor
├── travel_endpoint.py       # Travel search
├── files_endpoint.py        # File management
├── admin_endpoint.py        # Admin functions
├── core/                    # Core modules
│   ├── config.py           # Configuration
│   ├── auth.py             # Authentication
│   ├── helpers.py          # Utilities
│   ├── llm.py              # LLM integration
│   ├── memory.py           # STM/LTM/Psyche
│   ├── tools.py            # Internet tools
│   ├── research.py         # Auto-learning
│   ├── semantic.py         # Semantic analysis
│   ├── writing.py          # Text generation
│   └── executor.py         # Code execution
└── mrd/
    ├── .env                # Configuration
    └── mem.db              # Database
```

---

## 🔧 TROUBLESHOOTING:

### Port already in use:
```bash
python3 app.py --port 3000
```

### Missing dependencies:
```bash
pip install -r requirements.txt
```

### Database errors:
```bash
rm /workspace/mrd/mem.db
# Database będzie utworzona na nowo
```

### Check logs:
```bash
python3 app.py
# Logs będą w konsoli
```

---

## 💡 ADVANCED:

### Uruchom w tle:
```bash
nohup ./start.sh > server.log 2>&1 &
```

### Uruchom z systemd:
```ini
# /etc/systemd/system/mordzix.service
[Unit]
Description=Mordzix AI Full Auto
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/workspace
ExecStart=/workspace/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker:
```bash
docker build -t mordzix-ai .
docker run -p 8080:8080 -v /workspace/mrd:/workspace/mrd mordzix-ai
```

---

## 🎯 GŁÓWNE RÓŻNICE: `app.py` vs `monolit.py`

| Feature | app.py | monolit.py |
|---------|--------|------------|
| **Czystość** | ✅ Czysty, 250 linii | ❌ 6500+ linii |
| **Automatyzacja** | ✅ Pełna (STM→LTM, auto-learn, context) | ⚠️ Częściowa |
| **Endpointy** | ✅ Wszystkie | ✅ Wszystkie + legacy |
| **Czytelność** | ✅ Bardzo dobra | ⚠️ Skomplikowany |
| **Maintenance** | ✅ Łatwy | ❌ Trudny |
| **Rekomendacja** | ✅ **UŻYJ TEGO!** | ⚠️ Legacy |

---

## 🔥 WSZYSTKO DZIAŁA AUTO!

Teraz masz:
- ✅ Jeden plik główny (`app.py`)
- ✅ Wszystkie endpointy podłączone
- ✅ Pełna automatyzacja (STM→LTM, auto-learning, context)
- ✅ Prosty start (`./start.sh`)
- ✅ 53 routes zarejestrowanych

**ZERO RĘCZNEJ PRACY! 🎉**
