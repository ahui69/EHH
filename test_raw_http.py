#!/usr/bin/env python3
import sys
import asyncio
import httpx
sys.path.insert(0, "/workspace/mrd")

async def test_raw_http():
    from core.config import SERPAPI_KEY
    
    print("=== TEST RAW HTTP ===\n")
    
    # Test 1: DuckDuckGo
    print("1. DuckDuckGo:")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = "https://duckduckgo.com/html/"
            params = {"q": "test"}
            r = await client.get(url, params=params)
            print(f"   Status: {r.status_code}")
            print(f"   Length: {len(r.text)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: SERPAPI
    if SERPAPI_KEY:
        print("\n2. SERPAPI:")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = "https://serpapi.com/search.json"
                params = {"engine": "google", "q": "test", "api_key": SERPAPI_KEY}
                r = await client.get(url, params=params)
                print(f"   Status: {r.status_code}")
                print(f"   Response: {r.json() if r.status_code == 200 else r.text[:200]}")
        except Exception as e:
            print(f"   ERROR: {e}")
    
    # Test 3: Wikipedia
    print("\n3. Wikipedia:")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = "https://en.wikipedia.org/w/api.php"
            params = {"action": "query", "list": "search", "srsearch": "test", "format": "json"}
            r = await client.get(url, params=params)
            print(f"   Status: {r.status_code}")
            print(f"   Results: {len(r.json().get('query', {}).get('search', []))}")
    except Exception as e:
        print(f"   ERROR: {e}")

asyncio.run(test_raw_http())
