import requests
import json

# Poprawiona struktura żądania zgodnie z wymaganiami endpointu
response = requests.post(
    "http://162.19.220.29:8080/api/chat/assistant", 
    headers={
        "Content-Type": "application/json", 
        "Authorization": "Bearer ssjjMijaja6969"
    }, 
    json={
        "messages": [
            {
                "role": "user",
                "content": "Pokaż mi najnowsze wiadomości z Polski"
            }
        ],
        "conversation_id": "test-1234", 
        "options": {
            "stream": False, 
            "use_context": True, 
            "use_memory": True, 
            "fast_mode": False
        },
        "user_id": "test-user"
    }
)

print(json.dumps(response.json(), indent=2, ensure_ascii=False))