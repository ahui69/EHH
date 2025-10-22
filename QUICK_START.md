# 🚀 MORDZIX AI - QUICK START GUIDE

## ⚡ Szybkie uruchomienie (5 minut)

### 1️⃣ Stwórz plik `.env`

```bash
cp .env.example .env
```

Edytuj `.env` i ustaw **co najmniej** te wartości:

```bash
# WYMAGANE
LLM_API_KEY=twoj_klucz_deepinfra  # https://deepinfra.com (FREE 10k tokens/day!)
AUTH_TOKEN=twoj_tajny_token

# OPCJONALNE (może być puste)
WORKSPACE=/workspace
MEM_DB=/workspace/mem.db
```

### 2️⃣ Zainstaluj zależności

```bash
# Utwórz virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# lub
.venv\Scripts\activate  # Windows

# Zainstaluj pakiety
pip install -r requirements.txt

# Zainstaluj modele językowe
python -m spacy download pl_core_news_sm
```

### 3️⃣ Uruchom aplikację

**Opcja A: Prosty start (bez frontendu)**
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

**Opcja B: Pełny start z walidacją**
```bash
chmod +x start.sh
SKIP_FRONTEND_BUILD=1 ./start.sh
```

### 4️⃣ Otwórz w przeglądarce

```
http://localhost:8080
```

Gotowe! 🎉

---

## 🔑 Gdzie wziąć klucze API?

### DeepInfra (Polecane - FREE!)
1. Idź na: https://deepinfra.com
2. Zarejestruj się (GitHub lub email)
3. Dashboard → API Keys → Create API Key
4. Skopiuj klucz do `.env`

**FREE TIER:**
- 10,000 tokens dziennie
- Bez karty kredytowej
- Modele: Qwen, LLaMA, Mixtral

### Alternatywne providerzy:

**OpenAI** (Płatne)
- https://platform.openai.com/api-keys
- $5 minimum
- GPT-4, GPT-3.5

**Groq** (FREE!)
- https://console.groq.com
- Bardzo szybkie
- Mixtral, LLaMA

---

## 🧪 Testowanie

### Test API
```bash
# Health check
curl http://localhost:8080/health

# Test chat
curl -X POST http://localhost:8080/api/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Cześć Mordzix!"}
    ]
  }'
```

### Test interfejsu
1. Otwórz: http://localhost:8080
2. Napisz: "Cześć, kim jesteś?"
3. Sprawdź funkcje:
   - 🎤 Mikrofon (nagrywanie głosu)
   - 📎 Załączniki (obrazy, pliki)
   - 🔊 TTS (odczytywanie tekstu)
   - 📋 Kopiowanie odpowiedzi

---

## ❌ Rozwiązywanie problemów

### Problem: "LLM_API_KEY not set"
✅ **Rozwiązanie:** Ustaw klucz w `.env`

### Problem: "ModuleNotFoundError: No module named 'fastapi'"
✅ **Rozwiązanie:** 
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Problem: "Port 8080 already in use"
✅ **Rozwiązanie:**
```bash
# Zabij proces na porcie 8080
sudo lsof -t -i:8080 | xargs kill -9

# Lub użyj innego portu
python -m uvicorn app:app --port 8081
```

### Problem: "Frontend not found"
✅ **Rozwiązanie:** 
To nie jest błąd! Nowy minimalistyczny interfejs jest w `index_minimal.html` i działa bez budowania frontendu.

---

## 📚 Co dalej?

### Eksploruj funkcje:
- **Travel:** "Znajdź hotele w Krakowie"
- **Research:** "Sprawdź najnowsze wiadomości o AI"
- **Writing:** "Napisz artykuł o programowaniu"
- **Code:** "Wykonaj: ls -la"
- **Memory:** "Zapamiętaj że lubię pizzę"

### Dokumentacja API:
- Swagger: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### Monitoring:
- Status: http://localhost:8080/status
- Health: http://localhost:8080/health
- Metrics: http://localhost:8080/api/prometheus/metrics

---

## 🎯 Minimalne wymagania

- **Python:** 3.10+
- **RAM:** 512 MB (minimum), 2 GB (zalecane)
- **Disk:** 500 MB
- **Internet:** Wymagany (dla LLM API)

---

## 💰 Koszty

**FREE TIER (DeepInfra):**
- 10,000 tokens/dzień = ~7,500 słów
- ~150-200 wiadomości dziennie
- **0 PLN/miesiąc** 💸

**Płatne (opcjonalne):**
- OpenAI GPT-4: ~$0.03/1K tokens
- DeepInfra Pro: od $0.001/1K tokens

---

## 🆘 Pomoc

Masz problem? 
1. Sprawdź logi: `tail -f logs/mordzix.log`
2. Waliduj środowisko: `python core/env_validator.py`
3. Zobacz Issues: https://github.com/ahui69/aktywmrd/issues

---

**🔥 Built with ❤️ for easy AI deployment**
