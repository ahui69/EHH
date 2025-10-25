#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MORDZIX AI - Main Application Entry Point
Simple wrapper that runs core.app with proper environment setup
"""

import os
import sys
from pathlib import Path

# Ensure core module is in path
BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

# Set environment variables BEFORE importing core.app
os.environ.setdefault("AUTH_TOKEN", "ssjjMijaja6969")
os.environ.setdefault("WORKSPACE", str(BASE_DIR))
os.environ.setdefault("MEM_DB", str(BASE_DIR / "mem.db"))

# Import the main app from core (this has ALL the routers properly configured)
from core.app import app

# Initialize database on startup
@app.on_event("startup")
async def init_database():
    """Initialize memory database tables"""
    try:
        from core.advanced_memory import _init_db
        _init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[WARN] Database init: {e}")

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 MORDZIX AI - Starting from ROOT app.py wrapper")
    print("="*70)
    print(f"📁 Workspace: {BASE_DIR}")
    print(f"💾 Database: {os.getenv('MEM_DB')}")
    print("="*70 + "\n")
    
    # Production settings
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=False,  # Disable reload in production
        workers=1,     # Single worker for memory consistency
        log_level="info",
        access_log=True,
    )
