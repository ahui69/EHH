#!/bin/bash
# AUTOMATYCZNA NAPRAWA WSZYSTKIEGO - jedna komenda

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              🔧 AUTOMATYCZNA NAPRAWA SERWERA 🔧                      ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

cd /workspace/EHH/EHH || { echo "❌ Katalog nie istnieje!"; exit 1; }

# 1. Backup
echo "1️⃣ Backup..."
cp app.py app.py.backup.$(date +%s) 2>/dev/null
cp .env .env.backup.$(date +%s) 2>/dev/null

# 2. Pobierz najnowszy kod
echo "2️⃣ Pobieranie kodu z GitHub..."
git fetch origin
git checkout github-ready
git reset --hard origin/github-ready
echo "✅ Kod zaktualizowany"

# 3. Sprawdź pliki
echo ""
echo "3️⃣ Sprawdzam kluczowe pliki..."
FILES_OK=true
for file in app.py assistant_endpoint.py index_minimal.html core/cognitive_engine.py core/memory.py; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ BRAK: $file"
        FILES_OK=false
    fi
done

if [ "$FILES_OK" = false ]; then
    echo "❌ Brak kluczowych plików! Sprawdź git pull."
    exit 1
fi

# 4. Sprawdź/napraw .env
echo ""
echo "4️⃣ Sprawdzam .env..."
if [ ! -f .env ]; then
    echo "⚠️  Brak .env! Tworzę z .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Utworzono .env z .env.example"
    else
        echo "❌ Brak .env.example! Tworzę minimalny .env..."
        cat > .env << 'ENVEOF'
# Minimalna konfiguracja
WORKSPACE=/workspace/EHH/EHH
MEM_DB=/workspace/EHH/EHH/mem.db
UPLOAD_DIR=/workspace/EHH/EHH/uploads

# LLM - DODAJ SWÓJ KLUCZ!
LLM_BASE_URL=https://api.deepinfra.com/v1/openai
LLM_API_KEY=ZMIEN_MNIE_NA_PRAWDZIWY_KLUCZ
LLM_MODEL=Qwen/Qwen3-Next-80B-A3B-Instruct
LLM_TIMEOUT=60

# Auth
AUTH_TOKEN=ssjjMijaja6969

# Ports
BACKEND_PORT=8080
HOST=0.0.0.0
ENVEOF
        echo "⚠️  Utworzono minimalny .env - MUSISZ DODAĆ LLM_API_KEY!"
    fi
fi

# Sprawdź czy jest LLM_API_KEY
if grep -q "LLM_API_KEY=.\{10,\}" .env 2>/dev/null; then
    echo "✅ LLM_API_KEY jest ustawiony"
else
    echo "⚠️  LLM_API_KEY nie jest ustawiony lub za krótki!"
    echo "    Edytuj: nano .env"
fi

# 5. Uprawnienia do bazy
echo ""
echo "5️⃣ Sprawdzam bazę danych..."
if [ ! -f mem.db ]; then
    echo "⚠️  Brak mem.db - zostanie utworzona przy starcie"
else
    echo "✅ mem.db istnieje ($(ls -lh mem.db | awk '{print $5}'))"
    chmod 666 mem.db 2>/dev/null || true
fi

# 6. Test importu Python
echo ""
echo "6️⃣ Test importu modułów Python..."
python3 << 'PYTEST'
import sys
sys.path.insert(0, '/workspace/EHH/EHH')

errors = []
try:
    from assistant_endpoint import router as assistant_router
    print("   ✅ assistant_endpoint")
except Exception as e:
    print(f"   ❌ assistant_endpoint: {e}")
    errors.append("assistant_endpoint")

try:
    from core.cognitive_engine import cognitive_engine
    print("   ✅ cognitive_engine")
except Exception as e:
    print(f"   ❌ cognitive_engine: {e}")
    errors.append("cognitive_engine")

try:
    from core.memory import _save_turn_to_memory
    print("   ✅ memory")
except Exception as e:
    print(f"   ❌ memory: {e}")
    errors.append("memory")

if errors:
    print(f"\n⚠️  Błędy importu: {', '.join(errors)}")
    print("   Mogą być brakujące dependencies.")
    exit(0)  # Nie blokuj restartu
else:
    print("\n✅ Wszystkie moduły OK!")
PYTEST

# 7. Restart serwera
echo ""
echo "7️⃣ Restart serwera..."
sudo systemctl restart mordzix-ai
sleep 4

# 8. Status
echo ""
echo "8️⃣ Status serwera..."
if systemctl is-active --quiet mordzix-ai; then
    echo "✅ Serwer działa!"
else
    echo "❌ Serwer nie działa!"
    echo "Sprawdź logi: journalctl -u mordzix-ai -n 50 --no-pager"
fi

# 9. Logi
echo ""
echo "9️⃣ Ostatnie logi (szukam błędów)..."
journalctl -u mordzix-ai -n 50 --no-pager | grep -E "error|Error|ERROR|Exception|FAIL|✅|⏭" | tail -20

# 10. Test endpointów
echo ""
echo "🔟 Test endpointów..."
sleep 2

# Health
HEALTH=$(curl -s http://localhost:8080/health 2>/dev/null)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ /health działa"
else
    echo "   ❌ /health nie odpowiada"
fi

# Endpoints count
ENDPOINTS=$(curl -s http://localhost:8080/api/endpoints/list 2>/dev/null | grep -o '"count":[0-9]*' | cut -d: -f2)
if [ -n "$ENDPOINTS" ]; then
    echo "   📊 Endpointów: $ENDPOINTS"
    if [ "$ENDPOINTS" -gt 50 ]; then
        echo "   ✅ Routery załadowane!"
    else
        echo "   ⚠️  Za mało endpointów (powinno być 100+)"
    fi
else
    echo "   ❌ Nie mogę sprawdzić liczby endpointów"
fi

# Test chat
CHAT_TEST=$(curl -s -X POST http://localhost:8080/api/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}],"use_memory":true}' 2>/dev/null)

if echo "$CHAT_TEST" | grep -q "Brak API key"; then
    echo "   ⚠️  Chat działa ale brak LLM_API_KEY"
elif echo "$CHAT_TEST" | grep -q "answer"; then
    echo "   ✅ Chat działa!"
else
    echo "   ❌ Chat nie odpowiada poprawnie"
fi

# 11. Podsumowanie
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                        ✅ GOTOWE!                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Otwórz: http://162.19.220.29:8080"
echo "📚 Docs: http://162.19.220.29:8080/docs"
echo ""
echo "⚠️  Jeśli chat nie działa - dodaj LLM_API_KEY do .env:"
echo "   nano .env"
echo "   # Zmień LLM_API_KEY=... na prawdziwy klucz"
echo "   sudo systemctl restart mordzix-ai"
echo ""
