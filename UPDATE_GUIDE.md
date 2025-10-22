# 🔄 AKTUALIZACJA SERWERA Z GITHUB

## ⚡ NAJSZYBSZA METODA (1 KOMENDA)

```bash
cd /workspace/EHH/EHH && git pull && source .venv/bin/activate && pip install -r requirements.txt && sudo systemctl restart mordzix-ai && sudo systemctl status mordzix-ai
```

---

## 🔧 METODA Z SKRYPTEM (ZALECANA)

### **1. Pobierz skrypt (tylko raz):**
```bash
cd /workspace/EHH/EHH
wget https://raw.githubusercontent.com/ahui69/EHH/cursor/review-and-debug-first-code-aa54/update_server.sh
chmod +x update_server.sh
```

### **2. Uruchom aktualizację:**
```bash
./update_server.sh
```

**Skrypt automatycznie:**
- ✅ Zatrzymuje aplikację
- ✅ Pobiera zmiany z GitHub
- ✅ Aktualizuje dependencies
- ✅ Restartuje aplikację
- ✅ Sprawdza status

---

## 📝 METODA KROK PO KROKU

```bash
# 1. SSH do serwera
ssh ubuntu@vps-a3f42e4f

# 2. Przejdź do projektu
cd /workspace/EHH/EHH

# 3. Zatrzymaj aplikację
sudo systemctl stop mordzix-ai

# 4. Pobierz zmiany
git pull origin cursor/review-and-debug-first-code-aa54

# 5. Aktywuj venv
source .venv/bin/activate

# 6. Aktualizuj dependencies (jeśli były zmiany)
pip install -r requirements.txt --upgrade

# 7. Restart aplikacji
sudo systemctl restart mordzix-ai

# 8. Sprawdź status
sudo systemctl status mordzix-ai

# 9. Zobacz logi (opcjonalnie)
journalctl -u mordzix-ai -f
```

---

## 🚀 SZYBKIE KOMENDY

### **Aktualizuj bez zatrzymywania (hot reload):**
```bash
cd /workspace/EHH/EHH && git pull && sudo systemctl restart mordzix-ai
```

### **Aktualizuj z czyszczeniem cache:**
```bash
cd /workspace/EHH/EHH
git fetch --all
git reset --hard origin/cursor/review-and-debug-first-code-aa54
sudo systemctl restart mordzix-ai
```

### **Sprawdź co się zmieniło:**
```bash
cd /workspace/EHH/EHH
git fetch
git log HEAD..origin/cursor/review-and-debug-first-code-aa54 --oneline
```

### **Zobacz różnice przed aktualizacją:**
```bash
cd /workspace/EHH/EHH
git fetch
git diff HEAD origin/cursor/review-and-debug-first-code-aa54
```

---

## 🔄 AUTOMATYCZNA AKTUALIZACJA (CRON)

### **Ustaw auto-update co noc o 3:00:**

```bash
# Otwórz crontab
crontab -e

# Dodaj linię:
0 3 * * * cd /workspace/EHH/EHH && git pull && sudo systemctl restart mordzix-ai

# Zapisz: Ctrl+O, Enter, Ctrl+X
```

### **Lub z logami:**
```bash
0 3 * * * cd /workspace/EHH/EHH && git pull >> /var/log/mordzix-update.log 2>&1 && sudo systemctl restart mordzix-ai
```

---

## 🆘 TROUBLESHOOTING

### **Problem: "error: Your local changes would be overwritten"**
```bash
# Zapisz lokalne zmiany
cd /workspace/EHH/EHH
git stash

# Pobierz zmiany
git pull

# Przywróć lokalne (opcjonalnie)
git stash pop
```

### **Problem: "fatal: refusing to merge unrelated histories"**
```bash
cd /workspace/EHH/EHH
git pull origin cursor/review-and-debug-first-code-aa54 --allow-unrelated-histories
```

### **Problem: Aplikacja nie startuje po update**
```bash
# Sprawdź logi
journalctl -u mordzix-ai -n 50

# Sprawdź dependencies
cd /workspace/EHH/EHH
source .venv/bin/activate
pip install -r requirements.txt

# Sprawdź .env
nano .env

# Restart
sudo systemctl restart mordzix-ai
```

### **Przywróć poprzednią wersję:**
```bash
cd /workspace/EHH/EHH

# Zobacz commity
git log --oneline -5

# Wróć do poprzedniego
git checkout HEAD~1

# Restart
sudo systemctl restart mordzix-ai
```

---

## ✅ CHECKLIST AKTUALIZACJI

- [ ] SSH do serwera
- [ ] cd /workspace/EHH/EHH
- [ ] git pull
- [ ] pip install -r requirements.txt (jeśli były zmiany)
- [ ] sudo systemctl restart mordzix-ai
- [ ] sudo systemctl status mordzix-ai
- [ ] Sprawdź czy działa w przeglądarce
- [ ] Sprawdź logi (journalctl -u mordzix-ai -f)

---

## 🎯 NAJLEPSZE PRAKTYKI

1. **Zawsze rób backup przed aktualizacją:**
   ```bash
   cp -r /workspace/EHH/EHH /workspace/EHH/EHH.backup.$(date +%Y%m%d)
   ```

2. **Sprawdź co się zmienia przed pull:**
   ```bash
   git fetch
   git log HEAD..origin/cursor/review-and-debug-first-code-aa54
   ```

3. **Testuj na lokalnym przed wrzuceniem na serwer**

4. **Monitoruj logi po aktualizacji:**
   ```bash
   journalctl -u mordzix-ai -f
   ```

---

## 📊 MONITORING PO AKTUALIZACJI

```bash
# Status service
sudo systemctl status mordzix-ai

# Logi live
journalctl -u mordzix-ai -f

# Ostatnie 50 linii
journalctl -u mordzix-ai -n 50

# Sprawdź czy port działa
sudo netstat -tulpn | grep 8080

# Sprawdź procesy
ps aux | grep uvicorn

# Health check
curl http://localhost:8080/health
```

---

## 🔥 QUICK REFERENCE

```bash
# AKTUALIZUJ (1 linia)
cd /workspace/EHH/EHH && git pull && sudo systemctl restart mordzix-ai

# SPRAWDŹ STATUS
sudo systemctl status mordzix-ai

# LOGI
journalctl -u mordzix-ai -f

# RESTART
sudo systemctl restart mordzix-ai

# STOP
sudo systemctl stop mordzix-ai

# START
sudo systemctl start mordzix-ai
```

---

**GOTOWE!** 🚀

Teraz możesz łatwo aktualizować serwer z GitHuba!
