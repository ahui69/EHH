#!/bin/bash
# Pobierz i ustaw .env na serwerze

echo "🔧 Pobieranie .env z GitHub..."
cd /workspace/EHH/EHH

# Backup starego .env jeśli istnieje
if [ -f .env ]; then
    echo "💾 Backup starego .env..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Pobierz nowy
wget -O .env https://raw.githubusercontent.com/ahui69/EHH/cursor/review-and-debug-first-code-aa54/.env.production

echo "✅ .env pobrany i gotowy!"
echo ""
echo "🔄 Restart aplikacji:"
echo "sudo systemctl restart mordzix-ai"
