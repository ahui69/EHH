# ═══════════════════════════════════════════════════════════════════
# MORDZIX AI - ANGULAR FRONTEND QUICK START
# TYLKO LINUX! Deployment na serwerze OVH
# ═══════════════════════════════════════════════════════════════════

## 🐧 LINUX ONLY - DEPLOYMENT NA OVH

### KROK 1: Upload plików (z Windows - tylko raz)

```powershell
# Utwórz katalog na serwerze
ssh -i C:\Users\48501\.ssh\id_ed25519_ovh ubuntu@162.19.220.29 "sudo mkdir -p /workspace/mrd && sudo chown -R ubuntu:ubuntu /workspace"

# Prześlij pliki
scp -i C:\Users\48501\.ssh\id_ed25519_ovh -r C:\Users\48501\Desktop\mrd\* ubuntu@162.19.220.29:/workspace/mrd/
```

### KROK 2: SSH do serwera

```bash
ssh -i ~/.ssh/id_ed25519_ovh ubuntu@162.19.220.29
```

---

## 🚀 BUILD NA SERWERZE LINUX

```bash
# SSH do serwera
ssh -i ~/.ssh/id_ed25519_ovh ubuntu@162.19.220.29

# Zainstaluj Node.js (tylko raz)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Build frontend
cd /workspace/mrd/frontend
npm install
npm run build:prod
```

**Output:** `/workspace/mrd/frontend/dist/mordzix-ai/`

Backend (`app.py`) automatycznie serwuje te pliki z:
- `https://mordxixai.xyz/` → Angular SPA
- `https://mordxixai.xyz/docs` → API docs
- `https://mordxixai.xyz/api/*` → Backend API

---

## 📦 DEPLOY NA SERWER OVH (LINUX ONLY)

### Metoda 1: Automatyczny skrypt (RECOMMENDED)

```bash
# Na serwerze Linux
ssh -i ~/.ssh/id_ed25519_ovh ubuntu@162.19.220.29
cd /workspace/mrd
./update_frontend.sh
```

Skrypt automatycznie:
1. Sprawdza Node.js
2. Instaluje zależności (jeśli brak)
3. Buduje frontend (npm run build:prod)
4. Restartuje backend (supervisorctl restart mordzix)
5. Pokazuje status

### Metoda 2: Manualnie na serwerze

```bash
# 1. SSH
ssh -i ~/.ssh/id_ed25519_ovh ubuntu@162.19.220.29

# 2. Build
cd /workspace/mrd/frontend
npm run build:prod

# 3. Restart
sudo supervisorctl restart mordzix
```

### Metoda 3: Jedna komenda (quick)

```bash
ssh -i ~/.ssh/id_ed25519_ovh ubuntu@162.19.220.29 "cd /workspace/mrd/frontend && npm run build:prod && sudo supervisorctl restart mordzix"
```

---

## ✅ WERYFIKACJA

Po deploy sprawdź:

```bash
# Health
curl https://mordxixai.xyz/health

# Frontend (powinien zwrócić HTML)
curl -I https://mordxixai.xyz/

# Test chat
curl -X POST https://mordxixai.xyz/api/chat/assistant \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}],"user_id":"test","use_memory":false}'
```

Lub otwórz w przeglądarce: **https://mordxixai.xyz/**

---

## 📁 STRUKTURA PROJEKTU

```
frontend/
├── src/
│   ├── app/
│   │   ├── core/
│   │   │   ├── services/
│   │   │   │   ├── api.service.ts       # Komunikacja z backendem
│   │   │   │   └── chat.service.ts      # Zarządzanie wiadomościami
│   │   │   ├── guards/                  # Auth guards (future)
│   │   │   └── interceptors/            # HTTP interceptors (future)
│   │   ├── components/
│   │   │   ├── chat/                    # Główny komponent czatu
│   │   │   ├── header/                  # Header z menu
│   │   │   └── sidebar/                 # Sidebar z nawigacją
│   │   ├── shared/                      # Współdzielone komponenty
│   │   ├── app.component.*              # Root component
│   │   └── app.module.ts                # Główny moduł
│   ├── environments/
│   │   ├── environment.ts               # Dev (localhost:8080)
│   │   └── environment.prod.ts          # Prod (same host)
│   ├── assets/                          # Statyczne pliki
│   ├── styles.scss                      # Globalne style
│   ├── index.html                       # HTML template
│   └── main.ts                          # Bootstrap
├── angular.json                         # Angular config
├── tsconfig.json                        # TypeScript config
├── package.json                         # Dependencies
└── README.md                            # Dokumentacja frontendu
```

---

## 🔧 NPM SCRIPTS

```bash
npm start           # Dev server (localhost:4200)
npm run build       # Build development
npm run build:prod  # Build production (minified)
npm test            # Unit tests (future)
npm run lint        # Lint code (future)
```

---

## 🎨 DESIGN SYSTEM

### Kolory
- **Background**: `#000` (czarny)
- **Primary**: `#ff6600` (pomarańczowy)
- **Secondary**: `#4488ff` (niebieski)
- **Text**: `#fff` (biały)
- **Borders**: `#333` (ciemny szary)

### Komponenty
- **Header**: Gradient background, orange border-bottom
- **Sidebar**: Dark theme, slide animation
- **Chat Messages**: 
  - User: Orange left border
  - Assistant: Blue left border
  - Loading: Animated dots
- **Input Area**: Auto-resize textarea, orange send button

---

## 🔌 API INTEGRATION

### Endpoints używane przez frontend:

```typescript
// Chat
POST /api/chat/assistant
{
  "messages": [{"role":"user","content":"text"}],
  "user_id": "web_user",
  "use_memory": true,
  "auto_learn": true,
  "session_id": "optional"
}

// Health
GET /health

// Psyche
GET /api/psyche/status

// Memory
GET /api/memory/stats
POST /api/memory/search
```

### Auth Token
Każde żądanie zawiera header:
```
Authorization: Bearer ssjjMijaja6969
```

---

## 🐛 TROUBLESHOOTING

### Problem: npm install fails

```bash
# Usuń node_modules i spróbuj ponownie
rm -rf node_modules package-lock.json
npm install
```

### Problem: Build errors

```bash
# Clear cache
npm cache clean --force
rm -rf node_modules dist
npm install
npm run build:prod
```

### Problem: Backend nie serwuje frontendu

1. Sprawdź czy `frontend/dist/mordzix-ai/` istnieje
2. Zrestartuj backend: `python app.py`
3. Sprawdź logi: `sudo supervisorctl tail -f mordzix`

### Problem: CORS errors

Backend już ma CORS enabled. Jeśli problem występuje:
1. Sprawdź `environment.ts` - czy `apiUrl` jest poprawny?
2. Czy backend działa? `curl http://localhost:8080/health`

---

## 📚 PEŁNA DOKUMENTACJA

Zobacz: **DEPLOY_ANGULAR.md** - kompletna instrukcja krok-po-kroku

---

## 🎯 NASTĘPNE KROKI

1. ✅ Struktura projektu Angular - GOTOWE
2. ✅ Konfiguracja (package.json, tsconfig, angular.json) - GOTOWE
3. ✅ Serwisy (API, Chat) - GOTOWE
4. ✅ Komponenty (Chat, Header, Sidebar) - GOTOWE
5. ✅ Integracja z FastAPI - GOTOWE
6. ✅ Deploy scripts (PowerShell, Bash) - GOTOWE
7. ✅ Dokumentacja - GOTOWE

**STATUS: READY TO DEPLOY** 🚀

---

**Autor:** Mordzix AI Team  
**Wersja:** 5.0.0  
**Data:** 16.10.2025
