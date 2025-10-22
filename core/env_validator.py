#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Validator - sprawdza czy wszystkie wymagane zmienne są ustawione
"""

import os
import sys
from pathlib import Path


def validate_environment(strict: bool = False) -> bool:
    """
    Waliduje środowisko uruchomieniowe
    
    Args:
        strict: Jeśli True, kończy program gdy brakuje wymaganych zmiennych
        
    Returns:
        bool: True jeśli wszystko OK, False jeśli są problemy
    """
    print("\n" + "="*70)
    print("🔍 VALIDATING ENVIRONMENT")
    print("="*70 + "\n")
    
    # Sprawdź czy istnieje .env
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("⚠️  WARNING: .env file not found!")
        print(f"   Expected at: {env_path}")
        print("   Copy .env.example to .env and fill in your values")
        print()
    
    # Wymagane zmienne
    required = {
        "LLM_API_KEY": {
            "description": "LLM API Key (DeepInfra, OpenAI, etc.)",
            "link": "https://deepinfra.com",
            "critical": True
        }
    }
    
    # Opcjonalne ale zalecane
    recommended = {
        "AUTH_TOKEN": {
            "description": "Authentication token for API security",
            "default": "ssjjMijaja6969"
        },
        "SERPAPI_KEY": {
            "description": "Google Search API (optional)",
            "link": "https://serpapi.com"
        },
        "FIRECRAWL_API_KEY": {
            "description": "Web scraping API (optional)",
            "link": "https://firecrawl.dev"
        }
    }
    
    # Sprawdź wymagane
    missing_critical = []
    for key, info in required.items():
        value = os.getenv(key)
        if not value or value == "your_api_key_here" or value == "change_me":
            missing_critical.append((key, info))
            print(f"❌ {key}")
            print(f"   {info['description']}")
            if 'link' in info:
                print(f"   Get it here: {info['link']}")
            print()
    
    # Sprawdź zalecane
    missing_recommended = []
    for key, info in recommended.items():
        value = os.getenv(key)
        if not value or value == "your_api_key_here" or value == "change_me":
            missing_recommended.append((key, info))
            print(f"⚠️  {key} (optional)")
            print(f"   {info['description']}")
            if 'default' in info:
                print(f"   Using default: {info['default']}")
            if 'link' in info:
                print(f"   Get it here: {info['link']}")
            print()
    
    # Sprawdź ścieżki
    workspace = os.getenv("WORKSPACE", "/workspace")
    mem_db = os.getenv("MEM_DB", f"{workspace}/mem.db")
    upload_dir = os.getenv("UPLOAD_DIR", f"{workspace}/uploads")
    
    print("📁 Paths:")
    print(f"   WORKSPACE: {workspace}")
    print(f"   MEM_DB: {mem_db}")
    print(f"   UPLOAD_DIR: {upload_dir}")
    print()
    
    # Podsumowanie
    print("="*70)
    
    if missing_critical:
        print("❌ VALIDATION FAILED")
        print()
        print("Missing critical environment variables:")
        for key, info in missing_critical:
            print(f"  • {key}: {info['description']}")
        print()
        print("💡 To fix:")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your API keys")
        print("  3. Restart the application")
        print()
        
        if strict:
            sys.exit(1)
        return False
    
    if missing_recommended:
        print("⚠️  VALIDATION PASSED WITH WARNINGS")
        print()
        print(f"Missing {len(missing_recommended)} optional variables (app will work)")
        print()
    else:
        print("✅ VALIDATION PASSED")
        print()
    
    print("="*70 + "\n")
    return True


def get_env_summary() -> dict:
    """Zwraca podsumowanie konfiguracji środowiska"""
    return {
        "llm_configured": bool(os.getenv("LLM_API_KEY")),
        "auth_configured": bool(os.getenv("AUTH_TOKEN")),
        "serpapi_configured": bool(os.getenv("SERPAPI_KEY")),
        "firecrawl_configured": bool(os.getenv("FIRECRAWL_API_KEY")),
        "workspace": os.getenv("WORKSPACE", "/workspace"),
        "mem_db": os.getenv("MEM_DB"),
    }


if __name__ == "__main__":
    # Standalone run - strict mode
    validate_environment(strict=True)
