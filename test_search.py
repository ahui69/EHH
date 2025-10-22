#!/usr/bin/env python3
import sys
import asyncio
sys.path.insert(0, "/workspace/mrd")

async def test_search():
    from core.research import _search_all, _ddg_search, _serpapi_search
    from core.config import SERPAPI_KEY
    
    print(f"SERPAPI_KEY: {'SET' if SERPAPI_KEY else 'NOT SET'}")
    
    print("\n=== TEST DDG SEARCH ===")
    try:
        ddg_results = await _ddg_search("najnowsze wiadomości Polska", 5)
        print(f"DDG results: {len(ddg_results)}")
        for title, url in ddg_results[:3]:
            print(f"  - {title[:60]}... | {url[:50]}")
    except Exception as e:
        print(f"DDG ERROR: {e}")
    
    if SERPAPI_KEY:
        print("\n=== TEST SERPAPI SEARCH ===")
        try:
            serp_results = await _serpapi_search("najnowsze wiadomości Polska", 5)
            print(f"SERPAPI results: {len(serp_results)}")
            for title, url in serp_results[:3]:
                print(f"  - {title[:60]}... | {url[:50]}")
        except Exception as e:
            print(f"SERPAPI ERROR: {e}")
    
    print("\n=== TEST _search_all ===")
    try:
        all_results = await _search_all("najnowsze wiadomości Polska", "fast")
        print(f"TOTAL results: {len(all_results)}")
        for title, url in all_results[:5]:
            print(f"  - {title[:60]}... | {url[:50]}")
    except Exception as e:
        print(f"_search_all ERROR: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_search())
