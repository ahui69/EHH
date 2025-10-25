# Copilot — stałe instrukcje (twardy tryb, z SSH)

## ZASADY OGÓLNE (symulacja temp ~0.2)
- **Zero** TODO / placeholderów / pseudokodu.
- **Pełne, uruchamialne pliki**. Jeśli czegoś brakuje, **zaproponuj działający kontrakt i od razu go zaimplementuj + testy** (SQLite fallback, jawne modele, realne handlery).
- Zawsze dawaj **kompletne pliki** w blokach kodu (```python, ```tsx, itp.) ze **ścieżką**.
- Kolejność: **kroki → pełne pliki → komendy uruchomienia → testy → weryfikacja**.
- Błędy: własne **exception handlers** z ujednoliconym JSON-em.

## PIPELINE
1) Wygeneruj `analysis/endpoints_map.md` (plik → endpointy → modele → zależności).
2) Złóż kompletny `app.py` (FastAPI): routery, JWT+RBAC, Pydantic, error handlers, CORS, `/healthz`, `/metrics`, `/docs`, uploady, `.env`.
3) Front w `/frontend` (ChatGPT-style): lista rozmów, chat z SSE/WS, prawa kolumna settings, auth JWT, historia, eksport/import, obsługa błędów.
4) Testy (pytest + Playwright), `docker-compose.yml`, `.github/workflows/ci.yml`.
5) Podaj **komendy deploy** (nginx + systemd) i **sanity-check**.

## BEZPIECZEŃSTWO
- Walidacja (Pydantic), rate-limit per user+endpoint, CORS + CSP.
- Sekrety w `.env` (dodaj `.env.example`).
- Logi JSON z `request_id`. Health + readiness.

## 🚀 DOSTĘP SSH (zmiany online, obowiązkowo)
**Dev** generuje klucz **lokalnie** i podaje **tylko publiczny**. **Owner** (Ty) wkleja one-linera i podaje hasło.

**Szablon do wklejenia przez dev w PR/Issue:**
```
=== PUBLIC SSH KEY (only) ===
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... wykonawca@example

=== ONE-LINER (owner runs) ===
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... wykonawca@example' | ssh user@server "umask 0077 && mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"

=== CONNECT EXAMPLE (dev runs) ===
ssh -i /ścieżka/do/private_key -o IdentitiesOnly=yes user@server
```

**Usunięcie klucza po robocie:**
```
ssh user@server "cp ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bak && grep -v 'ssh-ed25519 AAAA...wykonawca' ~/.ssh/authorized_keys.bak > ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

## KRYTERIA AKCEPTACJI
- `app.py` w 100%, zero TODO.
- Front `/frontend`: chat (SSE/WS), auth, historia, eksport/import, obsługa błędów, dark mode.
- `docker-compose up --build` stawia cały stack.
- Testy przechodzą w CI.
- README + `.env.example` + OpenAPI kompletne.
- Działa **na żywym serwerze**.

## Jak użyć
Otwórz plik → **zaznacz wszystko** → w Copilot Chat kliknij **📌 Pin** („Pin selection to current chat prompt”).
