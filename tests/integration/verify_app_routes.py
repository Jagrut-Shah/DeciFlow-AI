import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(r"c:\Users\HP\Downloads\DeciFlow AI\backend"))

from app.main import app

print("--- Verifying app routes ---")
for route in app.routes:
    # FastAPI routes have 'path' attribute
    if hasattr(route, "path"):
        print(f"Path: {route.path}")

print("\n--- Verifying V1 router specifically ---")
from app.api.v1.router import api_router
for route in api_router.routes:
    if hasattr(route, "path"):
        print(f"V1 Path: {route.path}")
