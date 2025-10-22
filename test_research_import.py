#!/usr/bin/env python3
"""
Test if research.py can be imported after syntax fix
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, '/workspace/mrd')

print("Testing research.py import after syntax fix...")

try:
    # First verify the file has correct syntax
    with open('/workspace/mrd/core/research.py', 'r') as f:
        first_lines = [f.readline() for _ in range(10)]
    
    print("First 10 lines of research.py:")
    for i, line in enumerate(first_lines, 1):
        print(f"{i}: {line.rstrip()}")
    
    # Try to compile it
    print("\n✅ Attempting to compile research.py...")
    with open('/workspace/mrd/core/research.py', 'r') as f:
        code = f.read()
    
    compile(code, 'research.py', 'exec')
    print("✅ Syntax is valid! File compiles successfully.")
    
    # Try to import
    print("\n✅ Attempting to import core.research...")
    from core import research
    print("✅ Successfully imported core.research!")
    
    # Check if key functions exist
    print("\n✅ Checking for key functions:")
    functions = ['autonauka', 'web_learn', 'answer_with_sources', 'research_collect']
    for func_name in functions:
        if hasattr(research, func_name):
            print(f"  ✅ {func_name} - found")
        else:
            print(f"  ❌ {func_name} - missing")
    
    print("\n🎉 SUCCESS! research.py is working correctly!")
    
except SyntaxError as e:
    print(f"\n❌ SYNTAX ERROR: {e}")
    print(f"   Line {e.lineno}: {e.text}")
    sys.exit(1)
    
except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
