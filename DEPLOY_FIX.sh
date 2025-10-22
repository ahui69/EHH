#!/bin/bash
# DEPLOY FIX - uruchom na serwerze

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    🔧 NAPRAWIAM SERWER 🔧                            ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

cd /workspace/EHH/EHH || exit 1

# 1. Backup current state
echo "📦 Backup..."
cp app.py app.py.backup 2>/dev/null

# 2. Get latest code
echo "📥 Pobieranie najnowszego kodu..."
git fetch origin
git checkout github-ready
git reset --hard origin/github-ready

# 3. Check files
echo ""
echo "📊 Sprawdzam pliki..."
ls -lh app.py assistant_endpoint.py 2>/dev/null

# 4. Check .env
echo ""
echo "🔍 Sprawdzam .env..."
if [ ! -f .env ]; then
    echo "❌ BRAK .env! Tworzę z .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️  MUSISZ DODAĆ API KEYS DO .env!"
    fi
fi

# 5. Test Python imports
echo ""
echo "🐍 Test importu..."
python3 << 'PYTEST'
try:
    import sys
    sys.path.insert(0, '/workspace/EHH/EHH')
    from assistant_endpoint import router as assistant_router
    print("✅ assistant_endpoint import OK")
    
    from core.cognitive_engine import cognitive_engine  
    print("✅ cognitive_engine import OK")
    
    from core.memory import _save_turn_to_memory
    print("✅ memory import OK")
    
    print("\n🎉 WSZYSTKIE IMPORTY OK!")
except Exception as e:
    print(f"\n❌ IMPORT FAIL: {e}")
    import traceback
    traceback.print_exc()
PYTEST

# 6. Restart
echo ""
echo "🔄 Restart serwera..."
sudo systemctl restart mordzix-ai

sleep 3

# 7. Check status
echo ""
echo "📊 Status..."
sudo systemctl status mordzix-ai --no-pager | head -15

# 8. Check logs
echo ""
echo "📋 Ostatnie logi..."
journalctl -u mordzix-ai -n 30 --no-pager | tail -20

# 9. Test endpoint
echo ""
echo "🧪 Test endpointu..."
curl -s http://localhost:8080/health | jq .

echo ""
echo "✅ GOTOWE! Sprawdź http://162.19.220.29:8080"
