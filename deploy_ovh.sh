#!/bin/bash
#═══════════════════════════════════════════════════════════════════════
# MORDZIX AI - AUTO DEPLOYMENT NA OVH
#═══════════════════════════════════════════════════════════════════════
# Użycie: 
#   1. Upload na serwer: scp deploy_ovh.sh root@IP:/root/
#   2. SSH: ssh root@IP
#   3. Uruchom: chmod +x deploy_ovh.sh && ./deploy_ovh.sh
#═══════════════════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║         🚀 MORDZIX AI - DEPLOYMENT NA OVH 🚀                     ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Funkcje
print_step() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Sprawdź czy root
if [ "$EUID" -ne 0 ]; then 
    print_error "Uruchom jako root: sudo ./deploy_ovh.sh"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════
# KROK 1: UPDATE SYSTEMU
# ═══════════════════════════════════════════════════════════════════════
print_step "Aktualizacja systemu..."
apt update -y
apt upgrade -y

# ═══════════════════════════════════════════════════════════════════════
# KROK 2: INSTALACJA DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════
print_step "Instalacja Python, Nginx, Git..."
apt install -y python3 python3-pip python3-venv git nginx ufw curl

# Sprawdź Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_step "Python version: $PYTHON_VERSION"

if [ "$(echo "$PYTHON_VERSION < 3.9" | bc)" -eq 1 ]; then
    print_error "Python 3.9+ wymagany! Masz: $PYTHON_VERSION"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════
# KROK 3: KLONUJ PROJEKT
# ═══════════════════════════════════════════════════════════════════════
print_step "Klonowanie projektu z GitHub..."

if [ -d "/var/www/mordzix-ai" ]; then
    print_warning "Katalog /var/www/mordzix-ai już istnieje. Usuwam..."
    rm -rf /var/www/mordzix-ai
fi

mkdir -p /var/www
cd /var/www

git clone https://github.com/ahui69/EHH.git mordzix-ai
cd mordzix-ai
git checkout cursor/review-and-debug-first-code-aa54

print_step "Projekt sklonowany: /var/www/mordzix-ai"

# ═══════════════════════════════════════════════════════════════════════
# KROK 4: KONFIGURACJA .env
# ═══════════════════════════════════════════════════════════════════════
print_step "Tworzenie .env..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning ".env stworzony z .env.example"
    print_warning "MUSISZ EDYTOWAĆ .env I USTAWIĆ LLM_API_KEY!"
    echo ""
    echo "Edytuj teraz? (y/n)"
    read -r EDIT_ENV
    if [ "$EDIT_ENV" = "y" ]; then
        nano .env
    else
        print_warning "PAMIĘTAJ: edytuj .env później: nano /var/www/mordzix-ai/.env"
    fi
else
    print_step ".env już istnieje - używam istniejącego"
fi

# Ustaw ścieżki dla produkcji
sed -i 's|WORKSPACE=.*|WORKSPACE=/var/www/mordzix-ai|' .env
sed -i 's|MEM_DB=.*|MEM_DB=/var/www/mordzix-ai/mem.db|' .env
sed -i 's|UPLOAD_DIR=.*|UPLOAD_DIR=/var/www/mordzix-ai/uploads|' .env

# ═══════════════════════════════════════════════════════════════════════
# KROK 5: VIRTUAL ENV I DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════
print_step "Tworzenie virtual environment..."
python3 -m venv .venv

print_step "Aktywacja venv..."
source .venv/bin/activate

print_step "Upgrade pip..."
pip install --upgrade pip

print_step "Instalacja dependencies (to może chwilę potrwać)..."
pip install -r requirements.txt

# Spacy model (opcjonalnie)
print_step "Pobieranie spacy model (jeśli używany)..."
python3 -m spacy download pl_core_news_sm 2>/dev/null || print_warning "Spacy model nie zainstalowany (może nie być potrzebny)"

# Twórz katalogi
mkdir -p uploads logs
chmod 755 uploads logs

# ═══════════════════════════════════════════════════════════════════════
# KROK 6: WALIDACJA ŚRODOWISKA
# ═══════════════════════════════════════════════════════════════════════
print_step "Walidacja środowiska..."
python3 core/env_validator.py || print_warning "Walidacja zwróciła ostrzeżenia (sprawdź .env!)"

# ═══════════════════════════════════════════════════════════════════════
# KROK 7: NGINX CONFIG
# ═══════════════════════════════════════════════════════════════════════
print_step "Konfiguracja Nginx..."

cat > /etc/nginx/sites-available/mordzix-ai <<'EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

# Symlink
ln -sf /etc/nginx/sites-available/mordzix-ai /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test config
nginx -t

# Restart nginx
systemctl restart nginx
systemctl enable nginx

print_step "Nginx skonfigurowany i uruchomiony"

# ═══════════════════════════════════════════════════════════════════════
# KROK 8: SYSTEMD SERVICE
# ═══════════════════════════════════════════════════════════════════════
print_step "Tworzenie systemd service..."

cat > /etc/systemd/system/mordzix-ai.service <<'EOF'
[Unit]
Description=Mordzix AI - FastAPI Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/mordzix-ai
Environment="PATH=/var/www/mordzix-ai/.venv/bin"
ExecStart=/var/www/mordzix-ai/.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8080 --workers 2
Restart=always
RestartSec=10
StandardOutput=append:/var/log/mordzix-ai.log
StandardError=append:/var/log/mordzix-ai-error.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Start service
systemctl start mordzix-ai

# Enable auto-start
systemctl enable mordzix-ai

# Sprawdź status
sleep 2
if systemctl is-active --quiet mordzix-ai; then
    print_step "Service mordzix-ai uruchomiony ✅"
else
    print_error "Service nie działa! Sprawdź: systemctl status mordzix-ai"
fi

# ═══════════════════════════════════════════════════════════════════════
# KROK 9: FIREWALL
# ═══════════════════════════════════════════════════════════════════════
print_step "Konfiguracja firewall (ufw)..."

ufw allow 22/tcp  # SSH
ufw allow 80/tcp  # HTTP
ufw allow 443/tcp # HTTPS

# Enable (nieinteraktywnie)
echo "y" | ufw enable

print_step "Firewall skonfigurowany"

# ═══════════════════════════════════════════════════════════════════════
# KROK 10: SPRAWDŹ
# ═══════════════════════════════════════════════════════════════════════
print_step "Sprawdzanie czy aplikacja działa..."

sleep 3

# Health check
if curl -sf http://localhost:8080/health > /dev/null; then
    print_step "Health check: ✅ OK"
else
    print_warning "Health check: ❌ FAILED (może app się jeszcze uruchamia?)"
fi

# Get IP
SERVER_IP=$(curl -s ifconfig.me || echo "NIEZNANE_IP")

# ═══════════════════════════════════════════════════════════════════════
# FINALNE PODSUMOWANIE
# ═══════════════════════════════════════════════════════════════════════
echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║              ✅ DEPLOYMENT ZAKOŃCZONY! ✅                         ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🎉 Mordzix AI jest teraz LIVE na OVH!${NC}"
echo ""
echo "📍 Dostęp:"
echo "   http://$SERVER_IP"
if [ "$SERVER_IP" != "NIEZNANE_IP" ]; then
    echo "   (lub twoja domena jeśli skonfigurowałeś DNS)"
fi
echo ""
echo "🔧 Zarządzanie:"
echo "   Status:  systemctl status mordzix-ai"
echo "   Start:   systemctl start mordzix-ai"
echo "   Stop:    systemctl stop mordzix-ai"
echo "   Restart: systemctl restart mordzix-ai"
echo "   Logi:    journalctl -u mordzix-ai -f"
echo ""
echo "📁 Pliki:"
echo "   App:     /var/www/mordzix-ai"
echo "   Config:  /var/www/mordzix-ai/.env"
echo "   Nginx:   /etc/nginx/sites-available/mordzix-ai"
echo "   Service: /etc/systemd/system/mordzix-ai.service"
echo ""
echo "🔐 WAŻNE - NASTĘPNE KROKI:"
echo "   1. Sprawdź .env: nano /var/www/mordzix-ai/.env"
echo "   2. Ustaw LLM_API_KEY (https://deepinfra.com)"
echo "   3. Restart: systemctl restart mordzix-ai"
if [ "$SERVER_IP" != "NIEZNANE_IP" ]; then
    echo "   4. Otwórz: http://$SERVER_IP"
fi
echo ""
echo "🔒 SSL/HTTPS (opcjonalnie):"
echo "   apt install certbot python3-certbot-nginx"
echo "   certbot --nginx -d twoja-domena.pl"
echo ""
echo "💡 Aktualizacje:"
echo "   cd /var/www/mordzix-ai"
echo "   git pull"
echo "   systemctl restart mordzix-ai"
echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    🚀 ENJOY! 🚀                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
