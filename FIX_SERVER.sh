#!/bin/bash
echo "🔧 NAPRAWIAM SERWER..."
echo ""

# 1. Sprawdź branch
echo "1️⃣ Sprawdzam branch..."
git branch --show-current

# 2. Sprawdź czy app.py ma routery
echo ""
echo "2️⃣ Sprawdzam app.py..."
grep -c "app.include_router" app.py && echo "✅ Include router found" || echo "❌ Brak include_router!"

# 3. Sprawdź czy assistant_endpoint istnieje
echo ""
echo "3️⃣ Sprawdzam pliki..."
ls -lh assistant_endpoint.py 2>/dev/null && echo "✅ assistant_endpoint.py" || echo "❌ BRAK assistant_endpoint.py"
ls -lh core/cognitive_engine.py 2>/dev/null && echo "✅ cognitive_engine.py" || echo "❌ BRAK cognitive_engine"

# 4. Sprawdź .env
echo ""
echo "4️⃣ Sprawdzam .env..."
if [ -f .env ]; then
    grep "LLM_API_KEY=" .env | head -1 | sed 's/\(LLM_API_KEY=\).*/\1***HIDDEN***/'
    grep "MEM_DB=" .env
else
    echo "❌ BRAK .env!"
fi

# 5. Test importu
echo ""
echo "5️⃣ Test importu routerów..."
python3 -c "
try:
    from assistant_endpoint import router
    print('✅ assistant_endpoint import OK')
except Exception as e:
    print(f'❌ assistant_endpoint import FAIL: {e}')
    
try:
    from core.cognitive_engine import cognitive_engine
    print('✅ cognitive_engine import OK')
except Exception as e:
    print(f'❌ cognitive_engine import FAIL: {e}')
"

echo ""
echo "6️⃣ Sprawdzam aktualny commit..."
git log --oneline -1
