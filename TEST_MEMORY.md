# 🧠 TEST MEMORY - CO DOKŁADNIE SPRAWDZIĆ

## ✅ CO JEST W KODZIE (VERIFIED):

### 1. FRONTEND (index_minimal.html):
```javascript
// ZAWSZE wysyła:
use_memory: true
auto_learn: true
messages: [{ role: 'user', content: message }]
```

### 2. ASSISTANT_ENDPOINT.PY:
```python
# Import memory
from core.memory import _save_turn_to_memory, _auto_learn_from_turn

# Wywołuje cognitive_engine
result = await cognitive_engine.process_message(
    user_id=user_id,
    messages=[m.dict() for m in body.messages],
    req=req
)

# ZAPISUJE do memory
_save_turn_to_memory(plain_last_user, result["answer"], user_id)
if body.auto_learn:
    _auto_learn_from_turn(plain_last_user, result["answer"])
```

### 3. COGNITIVE_ENGINE.PY:
```python
# Import memory
from .memory import memory_manager
from .hierarchical_memory import hierarchical_memory_manager

# Wczytuje memory
memory_context = await self._load_memory_context(user_id, last_user_msg)

# Używa:
- stm_get_context()
- ltm_search_hybrid()
- psy_observe_text()
```

## 🔍 JAK PRZETESTOWAĆ NA SERWERZE:

### TEST 1: Pamięć w rozmowie
```
1. Napisz: "Nazywam się Jan"
2. Czekaj na odpowiedź
3. Napisz: "Jak mam na imię?"
```
**OCZEKIWANE:** AI odpowie "Jan" lub "Twoje imię to Jan"

### TEST 2: Sprawdź bazę danych
```bash
ssh ubuntu@162.19.220.29
cd /workspace/EHH/EHH
ls -lh mem.db
sqlite3 mem.db "SELECT COUNT(*) FROM memory;"
sqlite3 mem.db "SELECT * FROM memory ORDER BY ts DESC LIMIT 5;"
```

### TEST 3: Sprawdź logi
```bash
journalctl -u mordzix-ai -f | grep -i memory
```

### TEST 4: Sprawdź endpoint response
```bash
curl -X POST http://localhost:8080/api/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "test memory"}],
    "use_memory": true,
    "auto_learn": true
  }'
```

## ❓ MOŻLIWE PROBLEMY:

1. ❌ Baza danych nie istnieje lub nie ma uprawnień
2. ❌ .env nie ma MEM_DB lub ścieżka zła
3. ❌ cognitive_engine wywala exception (silent fail)
4. ❌ _save_turn_to_memory wywala exception (silent fail)
5. ❌ Router nie jest załadowany (ImportError)

## 🔧 GDZIE SPRAWDZIĆ:

1. **Na serwerze:**
   ```bash
   cd /workspace/EHH/EHH
   ls -la mem.db
   cat .env | grep MEM_DB
   ```

2. **Logi startu:**
   ```bash
   sudo systemctl restart mordzix-ai
   journalctl -u mordzix-ai -n 100 --no-pager
   ```
   Szukaj:
   - "✅ Chat (Advanced)"
   - "LOADING ENDPOINTS"
   - Errory związane z memory

3. **Test bezpośrednio:**
   ```bash
   cd /workspace/EHH/EHH
   python3 -c "from core.memory import _save_turn_to_memory; _save_turn_to_memory('test', 'odpowiedź', 'test_user'); print('✅ Memory działa!')"
   ```

## 🎯 CO ROBIĆ JEŚLI NIE DZIAŁA:

1. Sprawdź czy serwer ma najnowszy kod (git pull)
2. Sprawdź logi na błędy
3. Sprawdź czy mem.db istnieje i ma uprawnienia
4. Sprawdź czy .env ma MEM_DB
5. Restart serwera
