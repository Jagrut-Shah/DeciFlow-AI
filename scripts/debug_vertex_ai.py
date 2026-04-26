import asyncio
import sys
import os
import logging

# Set up paths
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.config import settings
from app.infrastructure.llm.vertex_adapter import VertexAdapter

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_vertex():
    print("--- Vertex AI Diagnostic ---")
    print(f"Project: {settings.GOOGLE_CLOUD_PROJECT}")
    print(f"Location: {settings.GOOGLE_CLOUD_LOCATION}")
    print(f"Credentials Path: {settings.GOOGLE_APPLICATION_CREDENTIALS_PATH}")
    
    # Check if credentials file exists
    cred_path = settings.GOOGLE_APPLICATION_CREDENTIALS_PATH
    if not os.path.isabs(cred_path):
        # Resolve like the adapter does
        root_dir = os.getcwd()
        abs_cred_path = os.path.abspath(os.path.join(root_dir, cred_path))
        print(f"Absolute Credential Path: {abs_cred_path}")
        if os.path.exists(abs_cred_path):
            print("[SUCCESS] Credentials file found.")
        else:
            print("[ERROR] Credentials file NOT found.")
    
    adapter = VertexAdapter()
    
    print("\nAttempting to generate content (Flash)...")
    try:
        response = await adapter.generate_content("Hello, this is a test from DeciFlow AI diagnostic script. Please respond with 'OK'.")
        if response:
            print(f"[SUCCESS] Response: {response}")
        else:
            print("[ERROR] Failure: Response was empty.")
    except Exception as e:
        print(f"[ERROR] during generation: {str(e)}")

    print("\nAttempting to generate structured insight...")
    try:
        test_data = {"total_sales": 1000, "total_profit": 300, "category": "Test"}
        response = await adapter.generate_structured_insight(test_data)
        if response:
            print(f"[SUCCESS] Insight: {response}")
        else:
            print("[ERROR] Failure: Insight was empty.")
    except Exception as e:
        print(f"[ERROR] during insight generation: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_vertex())
