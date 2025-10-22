# 🚀 MORDZIX AI - DEPLOYMENT NA OVH

## 📋 WYMAGANIA

**Serwer OVH (VPS/Dedicated):**
- Ubuntu 20.04+ / Debian 11+
- Min 2GB RAM
- Python 3.9+
- Dostęp SSH (root lub sudo)

**Lokalne:**
- SSH client
- Git

---

## 🔧 KROK 1: POŁĄCZ SIĘ Z SERWEREM

```bash
# SSH do twojego VPS
ssh root@twoj-serwer.ovh.net
# lub
ssh ubuntu@IP_SERWERA
```

**💡 Jeśli nie masz klucza SSH:**
```bash
# Na lokalnym komputerze:
ssh-keygen -t rsa -b 4096
ssh-copy-id root@IP_SERWERA
```

---

## 📦 KROK 2: INSTALACJA ZALEŻNOŚCI

```bash
# Update systemu
sudo apt update && sudo apt upgrade -y

# Python i narzędzia
sudo apt install -y python3 python3-pip python3-venv git nginx

# Sprawdź wersję Python
python3 --version
# Minimum: Python 3.9
```

---

## 📥 KROK 3: SKLONUJ PROJEKT

```bash
# Przejdź do katalogu aplikacji
cd /workspace/EHH

# Sklonuj repo
sudo git clone https://github.com/ahui69/EHH.git mordzix-ai
cd mordzix-ai

# Checkout do working branch
sudo git checkout cursor/review-and-debug-first-code-aa54

# Ustaw uprawnienia
sudo chown -R $USER:$USER /workspace/EHH/EHH
```

---

## 🔑 KROK 4: KONFIGURACJA

```bash
# Skopiuj .env
cp .env.example .env

# Edytuj .env
nano .env
```

**W .env ustaw:**
```bash
# WYMAGANE
LLM_API_KEY=twoj_klucz_z_deepinfra
AUTH_TOKEN=twoj_bezpieczny_token_do_api

# OPCJONALNE
SERPAPI_KEY=twoj_serpapi_key
FIRECRAWL_API_KEY=twoj_firecrawl_key

# PATHS (dla produkcji)
WORKSPACE=/workspace/EHH/EHH/EHH/EHH
MEM_DB=/workspace/EHH/EHH/mem.db
UPLOAD_DIR=/workspace/EHH/EHH/uploads

# LOG
LOG_LEVEL=INFO
LOG_TO_FILE=1
```

**Zapisz:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🐍 KROK 5: VIRTUAL ENV I DEPENDENCIES

```bash
# Stwórz venv
python3 -m venv .venv

# Aktywuj
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Instaluj dependencies
pip install -r requirements.txt

# Pobierz spacy model (jeśli używany)
python3 -m spacy download pl_core_news_sm || true

# Sprawdź środowisko
python3 core/env_validator.py
```

---

## 🔒 KROK 6: NGINX REVERSE PROXY

```bash
# Stwórz config nginx
sudo nano /etc/nginx/sites-available/mordzix-ai
```

**Wklej:**
```nginx
server {
    listen 80;
    server_name twoja-domena.pl www.twoja-domena.pl;
    # Lub IP: server_name 51.83.45.123;

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
```

**Aktywuj:**
```bash
# Symlink
sudo ln -s /etc/nginx/sites-available/mordzix-ai /etc/nginx/sites-enabled/

# Usuń default (opcjonalnie)
sudo rm /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 🔐 KROK 7: SSL (HTTPS) - OPCJONALNIE ALE ZALECANE

```bash
# Zainstaluj certbot
sudo apt install -y certbot python3-certbot-nginx

# Uzyskaj certyfikat (WYMAGA DOMENY!)
sudo certbot --nginx -d twoja-domena.pl -d www.twoja-domena.pl

# Automatyczne odnowienie
sudo certbot renew --dry-run
```

**Po tym nginx config będzie automatycznie zaktualizowany do HTTPS!**

---

## 🤖 KROK 8: SYSTEMD SERVICE (AUTO-START)

```bash
# Stwórz service
sudo nano /etc/systemd/system/mordzix-ai.service
```

**Wklej:**
```ini
[Unit]
Description=Mordzix AI - FastAPI Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/EHH/EHH
Environment="PATH=/workspace/EHH/EHH/.venv/bin"
ExecStart=/workspace/EHH/EHH/.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8080 --workers 2
Restart=always
RestartSec=10
StandardOutput=append:/var/log/mordzix-ai.log
StandardError=append:/var/log/mordzix-ai-error.log

[Install]
WantedBy=multi-user.target
```

**Zapisz i aktywuj:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start mordzix-ai

# Check status
sudo systemctl status mordzix-ai

# Enable auto-start
sudo systemctl enable mordzix-ai
```

---

## 📊 KROK 9: SPRAWDŹ CZY DZIAŁA

### **1. Sprawdź logi:**
```bash
# Live logs
sudo journalctl -u mordzix-ai -f

# Ostatnie 50 linii
sudo tail -50 /var/log/mordzix-ai.log
```

### **2. Test API:**
```bash
# Health check
curl http://localhost:8080/health

# Status
curl http://localhost:8080/status
```

### **3. Otwórz w przeglądarce:**
```
http://twoja-domena.pl
# lub
http://IP_SERWERA
```

**Powinien się załadować interfejs!** ✅

---

## 🔥 KROK 10: FIREWALL (BEZPIECZEŃSTWO)

```bash
# Zainstaluj ufw
sudo apt install -y ufw

# Zezwól na SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Włącz firewall
sudo ufw enable

# Sprawdź status
sudo ufw status
```

---

## 🔄 AKTUALIZACJE

**Gdy pushasz nowe zmiany na GitHub:**
```bash
# SSH do serwera
ssh root@twoj-serwer.ovh.net

# Przejdź do projektu
cd /workspace/EHH/EHH

# Pull zmian
git pull origin cursor/review-and-debug-first-code-aa54

# Restart service
sudo systemctl restart mordzix-ai

# Sprawdź
sudo systemctl status mordzix-ai
```

---

## 🛠️ UŻYTECZNE KOMENDY

### **Zarządzanie service:**
```bash
# Start
sudo systemctl start mordzix-ai

# Stop
sudo systemctl stop mordzix-ai

# Restart
sudo systemctl restart mordzix-ai

# Status
sudo systemctl status mordzix-ai

# Logi
sudo journalctl -u mordzix-ai -f
```

### **Sprawdź procesy:**
```bash
# Czy app działa?
ps aux | grep uvicorn

# Port 8080 używany?
sudo netstat -tulpn | grep 8080
```

### **Debug:**
```bash
# Sprawdź nginx
sudo nginx -t
sudo systemctl status nginx

# Sprawdź Python
cd /workspace/EHH/EHH
source .venv/bin/activate
python3 -c "from app import app; print('OK')"
```

---

## 📈 MONITORING (OPCJONALNIE)

### **1. PM2 (alternatywa dla systemd):**
```bash
# Instaluj pm2
sudo npm install -g pm2

# Start app
pm2 start "uvicorn app:app --host 127.0.0.1 --port 8080" --name mordzix-ai

# Auto-start
pm2 startup
pm2 save

# Monitor
pm2 monit
```

### **2. Logi rotacja:**
```bash
# Dodaj logrotate
sudo nano /etc/logrotate.d/mordzix-ai
```

```
/var/log/mordzix-ai*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}
```

---

## 🆘 TROUBLESHOOTING

### **Problem: "502 Bad Gateway"**
```bash
# Sprawdź czy app działa
sudo systemctl status mordzix-ai
sudo journalctl -u mordzix-ai -n 50

# Restart
sudo systemctl restart mordzix-ai
```

### **Problem: "Connection refused"**
```bash
# Sprawdź czy port 8080 jest otwarty
sudo netstat -tulpn | grep 8080

# Sprawdź firewall
sudo ufw status

# Sprawdź nginx
sudo nginx -t
sudo systemctl restart nginx
```

### **Problem: "ModuleNotFoundError"**
```bash
cd /workspace/EHH/EHH
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart mordzix-ai
```

### **Problem: "LLM_API_KEY not set"**
```bash
# Sprawdź .env
cat /workspace/EHH/EHH/.env | grep LLM_API_KEY

# Edytuj jeśli brak
nano /workspace/EHH/EHH/.env

# Restart
sudo systemctl restart mordzix-ai
```

---

## 🎯 QUICK DEPLOYMENT (COPY-PASTE WSZYSTKO)

```bash
#!/bin/bash
# MORDZIX AI - QUICK DEPLOY NA OVH

# Update systemu
sudo apt update && sudo apt upgrade -y

# Instaluj dependencies
sudo apt install -y python3 python3-pip python3-venv git nginx ufw

# Sklonuj projekt
cd /workspace/EHH
sudo git clone https://github.com/ahui69/EHH.git mordzix-ai
cd mordzix-ai
sudo git checkout cursor/review-and-debug-first-code-aa54
sudo chown -R $USER:$USER /workspace/EHH/EHH

# Stwórz .env
cp .env.example .env
echo "⚠️  EDYTUJ .env I USTAW LLM_API_KEY!"
nano .env

# Python setup
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Nginx config
sudo tee /etc/nginx/sites-available/mordzix-ai > /dev/null <<'EOF'
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
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/mordzix-ai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Systemd service
sudo tee /etc/systemd/system/mordzix-ai.service > /dev/null <<'EOF'
[Unit]
Description=Mordzix AI
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/EHH/EHH
Environment="PATH=/workspace/EHH/EHH/.venv/bin"
ExecStart=/workspace/EHH/EHH/.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start mordzix-ai
sudo systemctl enable mordzix-ai

# Firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo "y" | sudo ufw enable

# Status
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "Status: sudo systemctl status mordzix-ai"
echo "Logs: sudo journalctl -u mordzix-ai -f"
echo "URL: http://$(curl -s ifconfig.me)"
```

---

## ✅ CHECKLIST DEPLOYMENT

- [ ] Serwer OVH gotowy (SSH działa)
- [ ] Python 3.9+ zainstalowany
- [ ] Projekt sklonowany z GitHub
- [ ] .env skonfigurowany (LLM_API_KEY ustawiony!)
- [ ] Virtual env stworzony i dependencies zainstalowane
- [ ] Nginx zainstalowany i skonfigurowany
- [ ] Systemd service stworzony i uruchomiony
- [ ] Firewall skonfigurowany (porty 80, 443 otwarte)
- [ ] SSL/HTTPS skonfigurowany (certbot)
- [ ] Aplikacja dostępna przez przeglądarkę
- [ ] Logi działają poprawnie

---

## 🎉 GOTOWE!

**Twój Mordzix AI jest teraz LIVE na OVH!** 🚀

**Dostęp:**
```
http://twoja-domena.pl
http://IP_SERWERA
```

**Zarządzanie:**
```bash
sudo systemctl status mordzix-ai    # Status
sudo systemctl restart mordzix-ai   # Restart
sudo journalctl -u mordzix-ai -f    # Logi live
```

**Aktualizacje:**
```bash
cd /workspace/EHH/EHH
git pull
sudo systemctl restart mordzix-ai
```

---

## 💡 NASTĘPNE KROKI

1. **Custom domain:** Ustaw DNS A record na IP serwera
2. **HTTPS:** Uruchom `certbot --nginx -d twoja-domena.pl`
3. **Monitoring:** Zainstaluj pm2 lub uptime monitor
4. **Backups:** Regularnie backupuj `mem.db` i `uploads/`
5. **Scaling:** Zwiększ `--workers` w uvicorn dla większego ruchu

**ENJOY!** 💪
