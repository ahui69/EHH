#!/usr/bin/env python3
"""
Test API with correct endpoint after research.py fix
"""
import httpx
import json

API_URL = "http://162.19.220.29:8080"
AUTH_TOKEN = "ssjjMijaja6969"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

print("🧪 Testing API with CORRECT endpoint after research.py syntax fix\n")

# Test: Chat with web research trigger
print("🧪 Test: Chat with web research query...")
payload = {
    "messages": [
        {
            "role": "user",
            "content": "Jakie są najnowsze wiadomości z Polski?"
        }
    ],
    "user_id": "test_user",
    "use_memory": True,
    "use_research": True
}

try:
    r = httpx.post(f"{API_URL}/api/chat/assistant", json=payload, headers=headers, timeout=45)
    print(f"Status: {r.status_code}\n")
    
    if r.status_code == 200:
        data = r.json()
        
        print("=" * 70)
        print("✅ SUKCES! Odpowiedź otrzymana:\n")
        print(f"Answer: {data.get('answer', '')[:500]}...")
        print(f"\nProcessing time: {data.get('processing_time', 0):.2f}s")
        
        metadata = data.get('metadata', {})
        print(f"\nMetadata:")
        print(f"  - Confidence: {metadata.get('confidence', 0):.2f}")
        print(f"  - Originality: {metadata.get('originality', 0):.2f}")
        print(f"  - Cognitive mode: {metadata.get('cognitive_mode', 'unknown')}")
        print(f"  - Tools used: {metadata.get('tools_used', [])}")
        
        # Check if contains echo
        query_lower = payload["messages"][0]["content"].lower()
        answer_lower = data.get('answer', '').lower()
        
        # Check for problematic patterns
        if "obecnie nie mam dostępu" in answer_lower:
            print("\n⚠️ WARNING: Fallback odpowiedź 'nie mam dostępu'")
        elif "na podstawie dostępnego kontekstu nie mogę" in answer_lower:
            print("\n⚠️ WARNING: Fallback answer detected")
        elif query_lower in answer_lower and len(data.get('answer', '')) < 200:
            print("\n⚠️ WARNING: Possible echo of query in short response")
        else:
            print("\n✅ GOOD: Proper response generated (no fallback detected)")
        
        # Check sources
        sources = data.get('sources', [])
        if sources:
            print(f"\n✅ Sources provided: {len(sources)} items")
            for i, src in enumerate(sources[:3], 1):
                print(f"   {i}. {src.get('title', 'No title')[:50]}...")
        else:
            print("\n⚠️ No sources provided")
        
        print("=" * 70)
        
    else:
        print(f"❌ Error: {r.status_code}")
        print(f"Response: {r.text[:500]}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test complete!")
