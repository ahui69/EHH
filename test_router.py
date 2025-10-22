#!/usr/bin/env python3
import sys
import os
os.chdir('/workspace/mrd')
sys.path.insert(0, '/workspace/mrd')

from fastapi import FastAPI
import assistant_endpoint

app = FastAPI()
print("Routes before:", len(app.routes))

try:
    app.include_router(assistant_endpoint.router)
    print("include_router SUCCESS")
except Exception as e:
    print(f"include_router FAILED: {e}")

print("Routes after:", len(app.routes))

for route in app.routes:
    if hasattr(route, 'path') and 'chat' in route.path.lower():
        methods = getattr(route, 'methods', set())
        print(f"Found route: {route.path} Methods: {methods}")
