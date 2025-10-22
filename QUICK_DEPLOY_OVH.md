# ⚡ MORDZIX AI - QUICK DEPLOY NA OVH (3 MINUTY!)

## 🚀 NAJSZYBSZA METODA

### **KROK 1: SSH do serwera**
```bash
ssh root@twoj-serwer.ovh.net
# Lub: ssh ubuntu@IP_SERWERA
```

### **KROK 2: Pobierz i uruchom skrypt**
```bash
# Download deploy script
wget https://raw.githubusercontent.com/ahui69/EHH/cursor/review-and-debug-first-code-aa54/deploy_ovh.sh

# Ustaw uprawnienia
chmod +x deploy_ovh.sh

# URUCHOM
./deploy_ovh.sh
```

**Skrypt automatycznie:**
- ✅ Zainstaluje wszystkie dependencies
- ✅ Sklonuje projekt z GitHub
- ✅ Stworzy virtual environment
- ✅ Skonfiguruje Nginx
- ✅ Stworzy systemd service
- ✅ Ustawi firewall
- ✅ Uruchomi aplikację

### **KROK 3: Ustaw API KEY**
```bash
# Edytuj .env
nano /var/www/mordzix-ai/.env

# Znajdź i ustaw:
LLM_API_KEY=twoj_klucz_z_deepinfra

# Zapisz: Ctrl+O, Enter, Ctrl+X

# Restart
systemctl restart mordzix-ai
```

### **KROK 4: Otwórz w przeglądarce**
```
http://IP_TWOJEGO_SERWERA
```

**GOTOWE!** 🎉

---

## 🔑 GDZIE WZIĄĆ FREE API KEY?

1. Otwórz: https://deepinfra.com
2. Zarejestruj się (email + hasło)
3. Przejdź do: API Keys
4. Skopiuj klucz
5. Wklej do `.env`

**FREE tier:** 10,000 tokens/day!

---

## 🔒 HTTPS (SSL) - OPCJONALNIE

**Jeśli masz domenę:**
```bash
# Zainstaluj certbot
apt install -y certbot python3-certbot-nginx

# Uzyskaj certyfikat
certbot --nginx -d twoja-domena.pl -d www.twoja-domena.pl

# Gotowe! Nginx automatycznie skonfigurowany na HTTPS
```

---

## 🛠️ UŻYTECZNE KOMENDY

```bash
# Status aplikacji
systemctl status mordzix-ai

# Restart
systemctl restart mordzix-ai

# Logi live
journalctl -u mordzix-ai -f

# Sprawdź czy działa
curl http://localhost:8080/health

# Edytuj config
nano /var/www/mordzix-ai/.env

# Aktualizuj z GitHub
cd /var/www/mordzix-ai
git pull
systemctl restart mordzix-ai
```

---

## 🆘 PROBLEMY?

### **"502 Bad Gateway"**
```bash
# Sprawdź status
systemctl status mordzix-ai

# Sprawdź logi
journalctl -u mordzix-ai -n 50

# Restart
systemctl restart mordzix-ai
```

### **"LLM_API_KEY not set"**
```bash
# Sprawdź .env
cat /var/www/mordzix-ai/.env | grep LLM_API_KEY

# Edytuj
nano /var/www/mordzix-ai/.env

# Restart
systemctl restart mordzix-ai
```

### **"Connection refused"**
```bash
# Sprawdź czy port 8080 działa
netstat -tulpn | grep 8080

# Sprawdź nginx
nginx -t
systemctl restart nginx
```

---

## 📋 CHECKLIST

- [ ] SSH do serwera działa
- [ ] Uruchomiony `deploy_ovh.sh`
- [ ] Ustawiony `LLM_API_KEY` w `.env`
- [ ] Service uruchomiony: `systemctl status mordzix-ai`
- [ ] Nginx działa: `systemctl status nginx`
- [ ] Firewall otwarty: `ufw status`
- [ ] Aplikacja dostępna: `http://IP_SERWERA`
- [ ] HTTPS skonfigurowane (opcjonalnie)

---

## 🎯 ALTERNATYWNA METODA (RĘCZNIE)

Jeśli wolisz krok po kroku, zobacz: `DEPLOYMENT_OVH.md`

---

## ✅ PODSUMOWANIE

**3 KROKI:**
1. `./deploy_ovh.sh` - auto deployment
2. `nano .env` - ustaw LLM_API_KEY
3. `http://IP` - otwórz w przeglądarce

**DZIAŁA!** 🚀
