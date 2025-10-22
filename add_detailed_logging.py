#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dodaje szczegółowe logowanie do advanced_cognitive_engine.py
"""

def add_detailed_logging():
    filepath = '/workspace/mrd/core/advanced_cognitive_engine.py'
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Znajdź blok except Exception
    old_except = """        except Exception as e:
            log_error(f"[COGNITIVE_ENGINE] Błąd przetwarzania kognitywnego: {e}")
            return await self._create_fallback_result(user_message)"""
    
    new_except = """        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERROR][COGNITIVE_ENGINE] Błąd przetwarzania kognitywnego: {e}")
            print(f"[ERROR][COGNITIVE_ENGINE] Traceback:\\n{error_details}")
            with open('/tmp/cognitive_error.log', 'a') as f:
                f.write(f"\\n{'='*60}\\n")
                f.write(f"Timestamp: {time.time()}\\n")
                f.write(f"Error: {e}\\n")
                f.write(f"Traceback:\\n{error_details}\\n")
            return await self._create_fallback_result(user_message)"""
    
    if old_except in content:
        content = content.replace(old_except, new_except)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print('Dodano szczegółowe logowanie do advanced_cognitive_engine.py')
    else:
        print('Nie znaleziono bloku except do modyfikacji')

if __name__ == "__main__":
    add_detailed_logging()
