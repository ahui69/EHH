#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt debugujący metodę search_hybrid w hierarchical_memory.py
"""

import os
import sys
import time
import json

def debug_hierarchical_memory():
    """
    Dodaje pomocniczy kod debugujący do hierarchical_memory.py
    """
    filepath = '/workspace/mrd/core/hierarchical_memory.py'
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Sprawdź, czy metoda search_hybrid jest już zadekorowana debuggerem
    if 'DEBUG_SEARCH_HYBRID' in content:
        print('Kod debugujący jest już obecny!')
        return
    
    # Znajdź metodę search_hybrid
    search_pos = content.find('async def search_hybrid')
    if search_pos == -1:
        print('Nie znaleziono metody search_hybrid!')
        return
    
    # Znajdź koniec deklaracji metody
    end_of_declaration = content.find(')', search_pos)
    
    # Kod debugujący do wstawienia na początku metody
    debug_code = """
        # DEBUG_SEARCH_HYBRID - początek
        print(f"[DEBUG] search_hybrid wywołana z query='{query}', user_id='{user_id}', max_results={max_results}")
        try:
            with open('/tmp/search_hybrid_debug.log', 'a') as f:
                f.write(f"{time.time()}: search_hybrid(query='{query}', user_id='{user_id}', max_results={max_results})\\n")
        except Exception as e:
            print(f"[DEBUG] Błąd logowania: {e}")
        # DEBUG_SEARCH_HYBRID - koniec
        
    """
    
    # Znajdź początek implementacji metody (po zakończeniu deklaracji)
    method_body_start = content.find(':', end_of_declaration)
    if method_body_start == -1:
        print('Nie znaleziono ciała metody search_hybrid!')
        return
    
    # Znajdź początek pierwszej linii po deklaracji
    next_line_pos = content.find('\n', method_body_start) + 1
    
    # Wstaw kod debugujący na początek metody
    new_content = content[:next_line_pos] + debug_code + content[next_line_pos:]
    
    # Zapisz zmodyfikowany plik
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    # Dodaj także kod debugujący do pliku advanced_cognitive_engine.py
    engine_filepath = '/workspace/mrd/core/advanced_cognitive_engine.py'
    
    with open(engine_filepath, 'r') as f:
        engine_content = f.read()
    
    # Znajdź miejsce wywołania metody search_hybrid
    search_call_pos = engine_content.find('memory_results = await self.hierarchical_memory.search_hybrid')
    if search_call_pos == -1:
        print('Nie znaleziono wywołania metody search_hybrid w advanced_cognitive_engine.py!')
        return
    
    # Znajdź początek linii z wywołaniem
    line_start = engine_content.rfind('\n', 0, search_call_pos) + 1
    
    # Dodaj kod debugujący przed wywołaniem
    debug_engine_code = """        # DEBUG wywołanie search_hybrid
        try:
            print(f"[DEBUG] Przed wywołaniem search_hybrid w advanced_cognitive_engine")
            with open('/tmp/cognitive_debug.log', 'a') as f:
                f.write(f"{time.time()}: Próba wywołania search_hybrid(query='{user_message}', user_id='{user_id}')\\n")
        except Exception as e:
            print(f"[DEBUG] Błąd logowania w cognitive_engine: {e}")
        
"""
    
    # Wstaw kod debugujący przed wywołaniem search_hybrid
    new_engine_content = engine_content[:line_start] + debug_engine_code + engine_content[line_start:]
    
    # Zapisz zmodyfikowany plik cognitive_engine
    with open(engine_filepath, 'w') as f:
        f.write(new_engine_content)
    
    print('Pomyślnie dodano kod debugujący do obu plików!')

if __name__ == "__main__":
    debug_hierarchical_memory()