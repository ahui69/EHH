#!/bin/bash
# Cleanup niepotrzebnych plików

echo "🧹 Czyszczenie projektu..."

# Usuń duplikaty Python
rm -f app_full.py app_production.py app.py.backup app.py.broken app_simple.py
rm -f advanced_*.py analyze_logs.py add_*.py admin_*.py
rm -f batch_*.py captcha_*.py check_*.py debug_*.py
rm -f enhanced_prompts.py internal_ui.py monolit.py patch_backend.py routers_full.py
rm -f cleanup_verified.ps1

# Przenieś starą dokumentację
mkdir -p _docs
mv -f CHANGELOG_FIXES.md DASHBOARD_INFO.md DEPLOY_FINAL.md FINALNE_PODSUMOWANIE.md \
   FINAL_SUMMARY.md INTENT_DETECTION_STATUS.md PERSONALITIES.md \
   ULTRA_MINIMAL_SUMMARY.md UPGRADE_SUMMARY.md NOWE_SCIEZKI.txt \
   PATHS_UPDATED.md README_NAPRAWY.md _docs/ 2>/dev/null

# Usuń .pyc i cache
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "✅ Projekt wyczyszczony!"
echo ""
echo "📁 Struktura:"
ls -1 | grep -E "\.py$|\.html$|\.sh$|\.md$|^core$|^mrd$|^requirements" | head -20
