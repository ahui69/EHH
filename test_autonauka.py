#!/usr/bin/env python3
import sys
sys.path.insert(0, "/workspace/mrd")

print("=== TEST AUTONAUKA ===")
try:
    from core.research import autonauka
    print(f"✅ autonauka zaimportowana: {autonauka}")
    print(f"Type: {type(autonauka)}")
    
    # Test wywołania
    import asyncio
    
    async def test():
        print("\n=== TEST WYWOŁANIA ===")
        result = await autonauka("Pokaż mi najnowsze wiadomości z Polski", topk=3, deep_research=False, user_id="test")
        print(f"Wynik: {result}")
        return result
    
    result = asyncio.run(test())
    print(f"\n=== SUKCES ===")
    print(f"Answer: {result.get('answer', 'BRAK')[:200]}")
    print(f"Sources: {len(result.get('sources', []))}")
    
except Exception as e:
    print(f"❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
