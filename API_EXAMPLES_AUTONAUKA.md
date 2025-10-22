# Przykłady API - Autonauka w MRD AI

Ten dokument zawiera praktyczne przykłady wywołań API związanych z funkcjonalnością autonauki w systemie.

## Kluczowe funkcjonalności autonauki
1. **Dostęp do aktualnych informacji** - wiadomości, wyniki sportowe, artykuły
2. **Automatyczne uczenie** - system sam wykrywa brak wiedzy i uzupełnia ją
3. **Zapamiętywanie faktów** - znalezione informacje są zapisywane w LTM
4. **Wstrzykiwanie kontekstu** - znalezione fakty są używane do generowania odpowiedzi

## 1. Wywołanie czatu z autonauką

### Endpoint: `POST /api/chat/assistant`

### Parametry:
- `messages`: tablica wiadomości w formacie `{role, content}`
- `user_id`: identyfikator użytkownika
- `use_memory`: czy używać pamięci (STM/LTM)
- `auto_learn`: czy włączyć autonaukę
- `internet_allowed`: czy zezwolić na dostęp do internetu

### Przykład wywołania (curl):

```bash
curl -X POST "http://localhost:8080/api/chat/assistant" \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Opowiedz o najnowszych odkryciach w astronomii"}
    ],
    "user_id": "testuser123",
    "use_memory": true,
    "auto_learn": true,
    "internet_allowed": true
  }'
```

### Przykład wywołania (PowerShell):

```powershell
$headers = @{
    "Authorization" = "Bearer ssjjMijaja6969"
    "Content-Type" = "application/json"
}

$body = @{
    messages = @(
        @{
            role = "user"
            content = "Opowiedz o najnowszych odkryciach w astronomii"
        }
    )
    user_id = "testuser123"
    use_memory = $true
    auto_learn = $true
    internet_allowed = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/chat/assistant" -Method Post -Headers $headers -Body $body
```

### Przykład odpowiedzi:

```json
{
  "answer": "W ostatnich latach astronomia doświadczyła wielu przełomowych odkryć...",
  "user": "testuser123",
  "timestamp": 1698765432.123,
  "metadata": {
    "auto_learn": {
      "sources": [
        "https://www.nasa.gov/news/recent-discoveries/",
        "https://www.space.com/news"
      ],
      "facts_count": 12
    }
  }
}
```

## 2. Wywołanie wymuszonej autonauki

### Endpoint: `POST /api/chat/auto`

### Parametry:
- `query`: zapytanie/temat do nauki
- `user_id`: identyfikator użytkownika
- `force_learn`: czy wymusić naukę (nawet jeśli temat jest już znany)

### Przykład wywołania (curl):

```bash
curl -X POST "http://localhost:8080/api/chat/auto" \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Rozwój technologii kwantowych komputerów w 2023 roku",
    "user_id": "testuser123",
    "force_learn": true
  }'
```

### Przykład wywołania (PowerShell):

```powershell
$headers = @{
    "Authorization" = "Bearer ssjjMijaja6969"
    "Content-Type" = "application/json"
}

$body = @{
    query = "Rozwój technologii kwantowych komputerów w 2023 roku"
    user_id = "testuser123"
    force_learn = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/chat/auto" -Method Post -Headers $headers -Body $body
```

### Przykład odpowiedzi:

```json
{
  "ok": true,
  "answer": "W 2023 roku zanotowano znaczne postępy w rozwoju komputerów kwantowych...",
  "metadata": {
    "sources": [
      "https://www.nature.com/articles/quantum-computing-2023",
      "https://www.ibm.com/quantum/research"
    ],
    "facts_count": 8,
    "confidence": 0.87
  }
}
```

## 3. Wywołanie czatu strumieniowego z autonauką

### Endpoint: `POST /api/chat/assistant/stream`

### Parametry:
- `messages`: tablica wiadomości w formacie `{role, content}`
- `user_id`: identyfikator użytkownika
- `use_memory`: czy używać pamięci (STM/LTM)
- `auto_learn`: czy włączyć autonaukę
- `internet_allowed`: czy zezwolić na dostęp do internetu

### Przykład wywołania (JavaScript):

```javascript
async function streamChat() {
    const response = await fetch("http://localhost:8080/api/chat/assistant/stream", {
        method: "POST",
        headers: {
            "Authorization": "Bearer ssjjMijaja6969",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            messages: [
                {role: "user", content: "Opowiedz o najnowszych osiągnięciach w dziedzinie AI"}
            ],
            user_id: "testuser123",
            use_memory: true,
            auto_learn: true,
            internet_allowed: true
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const {value, done} = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, {stream: true});
        
        // Przetwarzanie buforowanych danych, szukanie kompletnych linii JSON
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Zachowanie niekompletnej linii
        
        for (const line of lines) {
            if (line.trim() === '') continue;
            try {
                const data = JSON.parse(line);
                console.log("Otrzymano fragment:", data);
                
                if (data.type === "metadata" && data.auto_learn) {
                    console.log("Źródła autonauki:", data.auto_learn.sources);
                }
            } catch (e) {
                console.error("Błąd parsowania JSON:", e);
            }
        }
    }
}

streamChat();
```

## 4. Sprawdzenie statusu autonauki

### Endpoint: `GET /api/chat/auto/status`

### Parametry:
- `user_id`: identyfikator użytkownika

### Przykład wywołania (curl):

```bash
curl -X GET "http://localhost:8080/api/chat/auto/status?user_id=testuser123" \
  -H "Authorization: Bearer ssjjMijaja6969"
```

### Przykład wywołania (PowerShell):

```powershell
$headers = @{
    "Authorization" = "Bearer ssjjMijaja6969"
}

Invoke-RestMethod -Uri "http://localhost:8080/api/chat/auto/status?user_id=testuser123" -Method Get -Headers $headers
```

### Przykład odpowiedzi:

```json
{
  "status": "idle",
  "last_query": "Rozwój technologii kwantowych komputerów w 2023 roku",
  "last_timestamp": 1698765432.123,
  "facts_count": 234,
  "sources_count": 15
}
```

## 5. Przykładowa integracja w JavaScript

```javascript
class AutonaukaManager {
    constructor(apiUrl, apiToken) {
        this.apiUrl = apiUrl;
        this.apiToken = apiToken;
        this.userId = localStorage.getItem('userId') || 'guest_' + Math.random().toString(36).substring(2, 9);
        
        // Zapisz userId
        localStorage.setItem('userId', this.userId);
    }
    
    async sendChatMessage(message, options = {}) {
        const defaults = {
            useMemory: true,
            autoLearn: true,
            internetAllowed: true
        };
        
        const settings = {...defaults, ...options};
        
        try {
            const response = await fetch(`${this.apiUrl}/api/chat/assistant`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${this.apiToken}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    messages: [{role: "user", content: message}],
                    user_id: this.userId,
                    use_memory: settings.useMemory,
                    auto_learn: settings.autoLearn,
                    internet_allowed: settings.internetAllowed
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error("Error sending chat message:", error);
            throw error;
        }
    }
    
    async forceLearn(query) {
        try {
            const response = await fetch(`${this.apiUrl}/api/chat/auto`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${this.apiToken}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    query: query,
                    user_id: this.userId,
                    force_learn: true
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error("Error forcing learn:", error);
            throw error;
        }
    }
    
    async getStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/api/chat/auto/status?user_id=${this.userId}`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${this.apiToken}`
                }
            });
            
            return await response.json();
        } catch (error) {
            console.error("Error getting autonauka status:", error);
            throw error;
        }
    }
}

// Przykład użycia
const autonauka = new AutonaukaManager("http://localhost:8080", "ssjjMijaja6969");

// Wysłanie wiadomości z autonauką
autonauka.sendChatMessage("Jakie są najnowsze odkrycia w dziedzinie astronomii?")
    .then(response => {
        console.log("Odpowiedź:", response.answer);
        
        if (response.metadata && response.metadata.auto_learn) {
            console.log("Źródła autonauki:", response.metadata.auto_learn.sources);
        }
    })
    .catch(error => console.error("Błąd:", error));

// Wymuszenie nauki na konkretny temat
autonauka.forceLearn("Historia rozwoju sztucznej inteligencji")
    .then(response => {
        if (response.ok) {
            console.log("Nauka zakończona sukcesem:", response.answer);
            console.log("Źródła:", response.metadata.sources);
        } else {
            console.error("Błąd podczas nauki:", response.error);
        }
    })
    .catch(error => console.error("Błąd:", error));
```

## 6. Testowanie autonauki za pomocą skryptu Python

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import argparse

def test_autonauka(base_url="http://localhost:8080", api_token="ssjjMijaja6969", user_id="test_user"):
    """Testuje funkcjonalność autonauki"""
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # 1. Test chat z włączoną autonauką
    print("\n1. Test chat z włączoną autonauką...")
    chat_payload = {
        "messages": [
            {"role": "user", "content": "Opowiedz o najnowszych odkryciach w astronomii w 2023 roku"}
        ],
        "user_id": user_id,
        "use_memory": True,
        "auto_learn": True,
        "internet_allowed": True
    }
    
    try:
        chat_response = requests.post(
            f"{base_url}/api/chat/assistant",
            headers=headers,
            json=chat_payload,
            timeout=30
        )
        
        chat_data = chat_response.json()
        print(f"Status: {chat_response.status_code}")
        print(f"Odpowiedź: {chat_data.get('answer', '')[:100]}...")
        
        if "metadata" in chat_data and "auto_learn" in chat_data["metadata"]:
            print(f"Autonauka aktywna: {len(chat_data['metadata']['auto_learn'].get('sources', []))} źródeł")
        else:
            print("Autonauka nie została uruchomiona")
            
    except Exception as e:
        print(f"Błąd podczas testu chat: {str(e)}")
    
    # 2. Test wymuszonej autonauki
    print("\n2. Test wymuszonej autonauki...")
    auto_payload = {
        "query": "Rozwój technologii kwantowych komputerów w 2023",
        "user_id": user_id,
        "force_learn": True
    }
    
    try:
        start_time = time.time()
        auto_response = requests.post(
            f"{base_url}/api/chat/auto",
            headers=headers,
            json=auto_payload,
            timeout=60
        )
        
        auto_data = auto_response.json()
        elapsed_time = time.time() - start_time
        
        print(f"Status: {auto_response.status_code}")
        print(f"Czas wykonania: {elapsed_time:.2f}s")
        print(f"OK: {auto_data.get('ok', False)}")
        
        if auto_data.get("ok", False):
            print(f"Odpowiedź: {auto_data.get('answer', '')[:100]}...")
            print(f"Liczba faktów: {auto_data.get('metadata', {}).get('facts_count', 0)}")
            print(f"Źródła: {auto_data.get('metadata', {}).get('sources', [])[:3]}")
        else:
            print(f"Błąd: {auto_data.get('error', 'Nieznany błąd')}")
            
    except Exception as e:
        print(f"Błąd podczas testu wymuszonej autonauki: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test autonauki w MORDZIX AI")
    parser.add_argument("--url", default="http://localhost:8080", help="Bazowy URL API")
    parser.add_argument("--token", default="ssjjMijaja6969", help="Token autoryzacyjny")
    parser.add_argument("--user", default="test_user", help="ID użytkownika")
    
    args = parser.parse_args()
    test_autonauka(args.url, args.token, args.user)
```

## 7. Przykłady korzystania z modułów dostępu do aktualnych danych

### Przykład wyszukiwania wiadomości

```bash
curl -X POST "http://localhost:8080/api/research/news" \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Najnowsze odkrycia w astronomii"
  }'
```

### Przykład odpowiedzi:

```json
{
  "ok": true,
  "items": [
    {
      "title": "Astronomowie odkryli nową planetę podobną do Ziemi",
      "link": "https://example.com/news/astronomy/new-earth-like-planet",
      "date": "2023-10-15"
    },
    {
      "title": "Teleskop James Webb dostarcza przełomowych odkryć",
      "link": "https://example.com/news/james-webb-telescope-discoveries",
      "date": "2023-10-10"
    }
  ]
}
```

### Wyszukiwanie informacji sportowych

```bash
curl -X POST "http://localhost:8080/api/chat/assistant" \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Jaki był wynik ostatniego meczu reprezentacji Polski?"}
    ],
    "user_id": "test_user",
    "use_memory": true,
    "auto_learn": true,
    "internet_allowed": true
  }'
```

### Wyszukiwanie informacji o atrakcjach turystycznych

```bash
curl -X POST "http://localhost:8080/api/travel/search" \
  -H "Authorization: Bearer ssjjMijaja6969" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Kraków", 
    "what": "attractions"
  }'
```

### Przykład odpowiedzi:

```json
{
  "ok": true,
  "center": {
    "lon": 19.944544,
    "lat": 50.06143
  },
  "items": [
    {
      "title": "Wawel",
      "address": "Wawel 5, Kraków",
      "rating": 4.8,
      "link": "https://maps.google.com/..."
    },
    {
      "title": "Rynek Główny",
      "address": "Rynek Główny, Kraków",
      "rating": 4.7,
      "link": "https://maps.google.com/..."
    }
  ]
}
```