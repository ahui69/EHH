╔═══════════════════════════════════════════════════════════════════════╗
║           🚀 MORDZIX AI - JAK URUCHOMIĆ NA OVH 🚀                    ║
╚═══════════════════════════════════════════════════════════════════════╝

⚡ NAJSZYBSZA METODA (3 MINUTY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  SSH DO SERWERA:
    ssh root@twoj-serwer.ovh.net

2️⃣  URUCHOM AUTO-DEPLOY:
    wget https://raw.githubusercontent.com/ahui69/EHH/cursor/review-and-debug-first-code-aa54/deploy_ovh.sh
    chmod +x deploy_ovh.sh
    ./deploy_ovh.sh

3️⃣  USTAW API KEY:
    nano /workspace/EHH/EHH/.env
    # Ustaw: LLM_API_KEY=twoj_klucz
    # Zapisz: Ctrl+O, Enter, Ctrl+X
    
    systemctl restart mordzix-ai

4️⃣  OTWÓRZ:
    http://IP_TWOJEGO_SERWERA

✅ GOTOWE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔑 GDZIE WZIĄĆ FREE API KEY:
    https://deepinfra.com → Register → API Keys (10k tokens/day FREE!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 SZCZEGÓŁOWA DOKUMENTACJA:
    • DEPLOYMENT_OVH.md - pełny przewodnik krok po kroku
    • QUICK_DEPLOY_OVH.md - szybki start
    • deploy_ovh.sh - automatyczny skrypt instalacyjny

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠️  ZARZĄDZANIE:
    systemctl status mordzix-ai      # Status
    systemctl restart mordzix-ai     # Restart
    journalctl -u mordzix-ai -f      # Logi live
    nano /workspace/EHH/EHH/.env    # Edytuj config

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 AKTUALIZACJE:
    cd /workspace/EHH/EHH
    git pull
    systemctl restart mordzix-ai

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 HTTPS (OPCJONALNIE):
    apt install -y certbot python3-certbot-nginx
    certbot --nginx -d twoja-domena.pl

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆘 PROBLEMY?
    # 502 Bad Gateway:
    systemctl restart mordzix-ai
    
    # Connection refused:
    systemctl restart nginx
    
    # LLM errors:
    nano /workspace/EHH/EHH/.env  # Sprawdź LLM_API_KEY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GitHub: https://github.com/ahui69/EHH
Branch: cursor/review-and-debug-first-code-aa54

ENJOY! 🎉
