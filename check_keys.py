#!/usr/bin/env python3
import sys
sys.path.insert(0, "/workspace/mrd")
from core.config import SERPAPI_KEY, FIRECRAWL_API_KEY

print(f"SERPAPI: {'SET (' + SERPAPI_KEY[:10] + '...)' if SERPAPI_KEY else 'NOT SET'}")
print(f"FIRECRAWL: {'SET (' + FIRECRAWL_API_KEY[:10] + '...)' if FIRECRAWL_API_KEY else 'NOT SET'}")
