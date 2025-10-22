#!/bin/bash
#
# URUCHOM TO NA SWOIM KOMPUTERZE!
#

SERVER="ubuntu@162.19.220.29"
SERVER_DIR="/workspace/EHH/EHH"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 KOPIOWANIE NAPRAWIONYCH PLIKÓW NA SERWER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Backup na serwerze
echo "1️⃣ Backup obecnych plików..."
ssh $SERVER "cd $SERVER_DIR && cp app.py app.py.backup-\$(date +%s) 2>/dev/null || true"

# Kopiuj pliki
echo "2️⃣ Kopiowanie app.py..."
scp app.py $SERVER:$SERVER_DIR/

echo "3️⃣ Kopiowanie suggestions_endpoint.py..."
scp suggestions_endpoint.py $SERVER:$SERVER_DIR/

echo "4️⃣ Kopiowanie batch_endpoint.py..."
scp core/batch_endpoint.py $SERVER:$SERVER_DIR/core/

echo "5️⃣ Kopiowanie index_minimal.html..."
scp index_minimal.html $SERVER:$SERVER_DIR/

# Restart
echo "6️⃣ Restart serwera..."
ssh $SERVER "sudo systemctl restart mordzix-ai"

echo ""
echo "7️⃣ Test..."
sleep 3
ssh $SERVER "curl -s http://localhost:8080/api/endpoints/list | grep count"

echo ""
echo "✅ GOTOWE!"
