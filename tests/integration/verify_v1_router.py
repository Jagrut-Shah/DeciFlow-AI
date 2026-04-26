import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(r"c:\Users\HP\Downloads\DeciFlow AI\backend"))

print("--- Verifying V1 router independently ---")
try:
    from app.api.v1.router import api_router
    for route in api_router.routes:
        if hasattr(route, "path"):
            print(f"V1 Path: {route.path}")
except Exception as e:
    print(f"Error importing router: {e}")
