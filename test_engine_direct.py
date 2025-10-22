#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test bezpośredni advanced_cognitive_engine"""
import sys
import traceback
sys.path.insert(0, "/workspace/mrd")

try:
    print("=== IMPORT MODUŁÓW ===")
    from core.advanced_cognitive_engine import get_advanced_cognitive_engine
    import asyncio
    
    print("=== INICJALIZACJA ENGINE ===")
    engine = get_advanced_cognitive_engine()
    
    print("=== TEST PROCESS_MESSAGE ===")
    
    async def test():
        try:
            result = await engine.process_message(
                user_message="Pokaż mi najnowsze wiadomości z Polski",
                user_id="test_user"
            )
            print(f"SUKCES! Odpowiedź: {result.primary_response[:100]}")
            return result
        except Exception as e:
            print(f"BŁĄD W process_message: {e}")
            traceback.print_exc()
            return None
    
    result = asyncio.run(test())
    
    if result:
        print(f"\n=== WYNIK ===")
        print(f"Confidence: {result.confidence_score}")
        print(f"Processing time: {result.total_processing_time}")
        print(f"Response: {result.primary_response[:200]}")
    
except Exception as e:
    print(f"KRYTYCZNY BŁĄD: {e}")
    traceback.print_exc()
