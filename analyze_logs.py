#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt do analizy logów
"""

import os
import sys

def analyze_log_file(filepath):
    """Analizuje plik logów, szukając informacji o błędach"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
        # Szukaj linii z błędami
        error_lines = []
        for line in content.split('\n'):
            if 'ERROR' in line or 'Exception' in line or 'Traceback' in line:
                error_lines.append(line)
                
        # Sprawdź ostatni błąd związany z advanced_cognitive_engine
        cognitive_errors = []
        for line in content.split('\n'):
            if ('cognitive' in line.lower() or 'engine' in line.lower()) and ('error' in line.lower() or 'exception' in line.lower()):
                cognitive_errors.append(line)
                
        print(f"Znaleziono {len(error_lines)} linii z błędami")
        print(f"Znaleziono {len(cognitive_errors)} linii z błędami dotyczącymi silnika kognitywnego")
        
        if error_lines:
            print("\n===== OSTATNIE BŁĘDY (max 10) =====")
            for line in error_lines[-10:]:
                print(line)
                
        if cognitive_errors:
            print("\n===== BŁĘDY SILNIKA KOGNITYWNEGO (max 10) =====")
            for line in cognitive_errors[-10:]:
                print(line)
                
    except Exception as e:
        print(f"Błąd analizy pliku: {e}")
        
if __name__ == "__main__":
    log_file = "/workspace/mrd/server_output.txt"
    if not os.path.exists(log_file):
        print(f"Plik {log_file} nie istnieje!")
        sys.exit(1)
        
    analyze_log_file(log_file)