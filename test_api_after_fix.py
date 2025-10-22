#!/usr/bin/env python3
"""
Test API after research.py syntax fix
"""
import httpx
import json
import time

API_URL = "http://162.19.220.29:8080"
AUTH_TOKEN = "ssjjMijaja6969"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

print("🧪 Testing API after research.py fix...\n")

# Wait for server to start
print("⏳ Waiting for server to start...")
time.sleep(5)

# Test 1: Health check
try:
    r = httpx.get(f"{API_URL}/api/health", timeout=10)
    print(f"✅ Health check: Status {r.status_code}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test 2: Chat with web research query
print("\n🧪 Testing chat with web research query...")
payload = {
    "message": "Jakie są najnowsze wiadomości z Polski?",
    "user_id": "test_user",
    "context": {}
}

try:
    r = httpx.post(f"{API_URL}/api/chat", json=payload, headers=headers, timeout=30)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"\n✅ Response received:")
        print(f"Answer: {data.get('answer', '')[:200]}...")
        print(f"Processing time: {data.get('processing_time', 0):.2f}s")
        print(f"Confidence: {data.get('metadata', {}).get('confidence', 0):.2f}")
        print(f"Metadata: {json.dumps(data.get('metadata', {}), indent=2, ensure_ascii=False)}")
        
        # Check if web research was used
        if 'web_research' in str(data.get('metadata', {})):
            print("\n✅ Web research was triggered!")
        else:
            print("\n⚠️ Web research was NOT triggered (might be using cached/LTM data)")
        
        # Check for echo fallback
        if payload["message"].lower() in data.get('answer', '').lower():
            print("\n⚠️ WARNING: Response might contain echo of query")
        else:
            print("\n✅ No echo detected - proper response generated")
            
    else:
        print(f"❌ Error: {r.status_code}")
        print(f"Response: {r.text}")
        
except Exception as e:
    print(f"❌ Chat test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ API test complete!")
