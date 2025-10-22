#!/bin/bash
#
# URUCHOM TO NA SWOIM KOMPUTERZE (nie tutaj!)
# Te komendy naprawią serwer OVH
#

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 NAPRAWIANIE SERWERA OVH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "KROK 1: Zaloguj się na serwer"
echo ""
echo "ssh ubuntu@162.19.220.29"
echo "(wpisz hasło gdy poprosi)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "KROK 2: Po zalogowaniu, uruchom:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "cd /workspace/EHH/EHH"
echo "git fetch origin"
echo "git checkout github-ready"
echo "git pull origin github-ready"
echo "bash NAPRAW_ONLINE.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "ALBO JEDNA KOMENDA (po ssh):"
echo ""
echo "cd /workspace/EHH/EHH && git fetch origin && git checkout github-ready && git pull origin github-ready && bash NAPRAW_ONLINE.sh"
