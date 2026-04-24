import os
import sys
from google import genai

# Add project root to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.config import settings

def list_models():
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    print("🔍 Fetching available models for your API Key...")
    for m in client.models.list():
        print(f" - {m.name}")

if __name__ == "__main__":
    list_models()
