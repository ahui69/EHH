@echo off
REM Prosty skrypt uruchomieniowy Mordzix AI dla Windows

echo ================================================================
echo          MORDZIX AI - SIMPLE START (WINDOWS)
echo ================================================================
echo.

REM 1. Sprawdz Python
echo [1/5] Sprawdzam Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python nie znaleziony! Zainstaluj Python 3.10+
    pause
    exit /b 1
)
python --version
echo [OK] Python znaleziony
echo.

REM 2. Sprawdz .env
echo [2/5] Sprawdzam .env...
if not exist ".env" (
    echo [ERROR] Brak pliku .env!
    if exist ".env.example" (
        echo Kopiuje .env.example do .env...
        copy .env.example .env
        echo [WARN] WAZNE: Edytuj .env i ustaw LLM_API_KEY!
        pause
    ) else (
        echo [ERROR] Brak .env.example! Nie moge kontynuowac.
        pause
        exit /b 1
    )
)
echo [OK] Plik .env istnieje
echo.

REM 3. Utworz venv
echo [3/5] Sprawdzam virtual environment...
if not exist ".venv" (
    echo Tworze .venv...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
echo [OK] Virtual environment aktywny
echo.

REM 4. Zainstaluj dependencies
echo [4/5] Instaluje zaleznosci...
python -m pip install --quiet --upgrade pip wheel
python -m pip install --quiet -r requirements.txt
echo [OK] Zaleznosci zainstalowane
echo.

REM 5. Waliduj srodowisko
echo [5/5] Walidacja srodowiska...
python core\env_validator.py
echo.

REM 6. Utworz katalogi
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs

REM 7. Uruchom
echo ================================================================
echo              MORDZIX AI URUCHOMIONY!
echo ================================================================
echo.
echo Interfejs:  http://localhost:8080
echo API Docs:   http://localhost:8080/docs
echo Zatrzymaj:  Ctrl+C
echo.

python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload

pause
