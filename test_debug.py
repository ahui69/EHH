#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test czy search_hybrid działa poprawnie z włączonym debugowaniem
"""
import requests
import json
import sys
import time

# Konfiguracja
URL = "http://localhost:8080/api/chat/assistant"
AUTH_TOKEN = "ssjjMijaja6969"

# Przygotuj nagłówki
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Przygotuj zapytanie z flagą debug
data = {
    "user_message": "Pokaż mi najnowsze wiadomości z Polski",
    "user_id": "test_user",
    "session_id": "test_session_debug",
    "messages": [
        {"role": "user", "content": "Pokaż mi najnowsze wiadomości z Polski"}
    ],
    "include_sources": True,
    "include_metadata": True,
    "debug": True  # Włącz tryb debug
}

# Zapisz początkową godzinę do znalezienia logów
start_time = time.strftime("%H:%M:%S")
print(f"Test rozpoczęty o: {start_time}")

# Wykonaj zapytanie
print("Wysyłanie zapytania...")
try:
    response = requests.post(URL, headers=headers, json=data, timeout=30)
    
    # Wyświetl wyniki
    print(f"Status: {response.status_code}")
    result = response.json()
    print("Odpowiedź:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Sprawdź logi po zapytaniu
    print("\nSzukam logów po czasie:", start_time)
    
except Exception as e:
    print(f"Błąd: {e}")
    sys.exit(1)