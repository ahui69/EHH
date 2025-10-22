#!/bin/bash
# Prosty skrypt uruchomieniowy Mordzix AI (bez frontendu Angular)

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🚀 MORDZIX AI - SIMPLE START 🚀                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Kolory
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Sprawdź Python
echo -e "${YELLOW}[1/5] Sprawdzam Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 nie znaleziony! Zainstaluj Python 3.10+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ ${PYTHON_VERSION}${NC}"

# 2. Sprawdź .env
echo -e "${YELLOW}[2/5] Sprawdzam .env...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Brak pliku .env!${NC}"
    echo -e "${YELLOW}Tworzę z .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  WAŻNE: Edytuj .env i ustaw LLM_API_KEY!${NC}"
        echo -e "${YELLOW}   Naciśnij Enter gdy będzie gotowe...${NC}"
        read
    else
        echo -e "${RED}❌ Brak .env.example! Nie mogę kontynuować.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Plik .env istnieje${NC}"

# 3. Utwórz venv jeśli nie istnieje
echo -e "${YELLOW}[3/5] Sprawdzam virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Tworzę .venv...${NC}"
    python3 -m venv .venv
fi
source .venv/bin/activate
echo -e "${GREEN}✅ Virtual environment aktywny${NC}"

# 4. Zainstaluj dependencies
echo -e "${YELLOW}[4/5] Instaluję zależności...${NC}"
pip install --quiet --upgrade pip wheel
pip install --quiet -r requirements.txt
echo -e "${GREEN}✅ Zależności zainstalowane${NC}"

# 5. Waliduj środowisko
echo -e "${YELLOW}[5/5] Walidacja środowiska...${NC}"
python3 core/env_validator.py || true

# 6. Utwórz katalogi
mkdir -p uploads logs

# 7. Zabij stare sesje
pkill -9 -f "uvicorn.*app:app" 2>/dev/null || true
sleep 1

# 8. Uruchom
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🚀 MORDZIX AI URUCHOMIONY! 🚀                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📍 Interfejs:${NC}  http://localhost:8080"
echo -e "${YELLOW}📚 API Docs:${NC}   http://localhost:8080/docs"
echo -e "${YELLOW}🔧 Zatrzymaj:${NC}  Ctrl+C"
echo ""

python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
