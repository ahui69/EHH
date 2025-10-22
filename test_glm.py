import httpx, os, json

LLM_BASE_URL = "https://api.deepinfra.com/v1/openai"
LLM_API_KEY = "w52XW0XN6zoV9hdY8OONhLu6tvnFaXbZ"
LLM_MODEL = "Qwen/Qwen3-Next-80B-A3B-Instruct"

client = httpx.Client(timeout=httpx.Timeout(120.0))
resp = client.post(
    f"{LLM_BASE_URL}/chat/completions",
    headers={
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": "Powiedz elo"}],
        "stream": False
    }
)
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
