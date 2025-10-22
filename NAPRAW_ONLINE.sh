#!/bin/bash
#
# SKRYPT DO URUCHOMIENIA NA SERWERZE OVH
# Skopiuj ten plik na serwer i uruchom:
# bash NAPRAW_ONLINE.sh
#

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 NAPRAWA SERWERA ONLINE - START"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /workspace/EHH/EHH || { echo "❌ Brak katalogu /workspace/EHH/EHH"; exit 1; }

echo "1️⃣ Backup obecnego kodu..."
cp app.py app.py.backup-$(date +%s) 2>/dev/null || true

echo "2️⃣ Git fetch..."
git fetch origin

echo "3️⃣ Checkout github-ready..."
git checkout github-ready

echo "4️⃣ Git pull..."
git pull origin github-ready

echo "5️⃣ Sprawdzam pliki..."
ls -lh app.py suggestions_endpoint.py core/batch_endpoint.py index_minimal.html

echo "6️⃣ Sprawdzam .env..."
if [ ! -f .env ]; then
    echo "⚠️ Brak .env - tworzę..."
    cat > .env << 'ENVEOF'
WORKSPACE=/workspace/EHH/EHH
MEM_DB=/workspace/EHH/EHH/mem.db
UPLOAD_DIR=/workspace/EHH/EHH/uploads

LLM_BASE_URL=https://api.deepinfra.com/v1/openai
LLM_API_KEY=ZMIEN_MNIE_NA_PRAWDZIWY_KLUCZ
LLM_MODEL=Qwen/Qwen3-Next-80B-A3B-Instruct
LLM_TIMEOUT=60

AUTH_TOKEN=ssjjMijaja6969
BACKEND_PORT=8080
HOST=0.0.0.0

SERPAPI_KEY=1ad52e9d1bf86ae9bbc32c3782b1ddf1cecc5f274fefa70429519a950bcfd2eb
FIRECRAWL_API_KEY=fc-ec025f3a447c6878bee6926b49c17d
ENVEOF
    echo "⚠️ MUSISZ ZMIENIĆ LLM_API_KEY W .env!"
else
    echo "✅ .env istnieje"
fi

echo "7️⃣ Test importów Python..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/EHH/EHH')

try:
    from app import app
    print("✅ app.py import OK")
except Exception as e:
    print(f"❌ app.py: {e}")
    sys.exit(1)

try:
    from assistant_endpoint import router
    print("✅ assistant_endpoint OK")
except Exception as e:
    print(f"❌ assistant: {e}")

api_routes = [r for r in app.routes if hasattr(r, 'path') and r.path.startswith('/api')]
print(f"✅ {len(api_routes)} API endpoints załadowanych")
PYEOF

echo ""
echo "8️⃣ Restart serwera..."
sudo systemctl restart mordzix-ai || echo "⚠️ Nie udało się zrestartować - sprawdź service"

echo ""
echo "9️⃣ Status serwera..."
sleep 3
sudo systemctl status mordzix-ai --no-pager -l | tail -20

echo ""
echo "🔟 Test endpointów..."
sleep 2
curl -s http://localhost:8080/api/endpoints/list | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'📊 Endpointów: {d[\"count\"]}')"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ NAPRAWA ZAKOŃCZONA!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️ Jeśli pokazuje 'ZMIEN_MNIE_NA_PRAWDZIWY_KLUCZ':"
echo "   nano .env"
echo "   (zmień LLM_API_KEY na prawdziwy)"
echo "   sudo systemctl restart mordzix-ai"
