#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test czy search_hybrid działa poprawnie
"""
import requests
import json
import sys

# Konfiguracja
URL = "http://localhost:8080/api/chat/assistant"
AUTH_TOKEN = "ssjjMijaja6969"

# Przygotuj nagłówki
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Przygotuj zapytanie
data = {
    "user_message": "Pokaż mi najnowsze wiadomości z Polski",
    "user_id": "test_user",
    "session_id": "test_session_123456",
    "messages": [
        {"role": "user", "content": "Pokaż mi najnowsze wiadomości z Polski"}
    ],
    "include_sources": True,
    "include_metadata": True
}

# Wykonaj zapytanie
print("Wysyłanie zapytania...")
try:
    response = requests.post(URL, headers=headers, json=data, timeout=30)
    
    # Wyświetl wyniki
    print(f"Status: {response.status_code}")
    result = response.json()
    print("Odpowiedź:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if "answer" in result:
        print("\nPoczątekowe 50 znaków odpowiedzi:")
        print(result["answer"][:50])
        
        # Sprawdź czy odpowiedź zawiera echo zapytania
        if "Pokaż mi najnowsze wiadomości z Polski" in result["answer"]:
            print("\nUWAGA: Odpowiedź zawiera echo zapytania - fallback jest nadal aktywny!")
        else:
            print("\nSUKCES: Odpowiedź nie zawiera echa zapytania - problem naprawiony!")
            
except Exception as e:
    print(f"Błąd: {e}")
    sys.exit(1)