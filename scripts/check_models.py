import asyncio
import os
import sys
from google.cloud import aiplatform

# Add project root to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

async def list_available_models():
    from app.core.config import settings
    
    # Initialize SDK
    if settings.GOOGLE_APPLICATION_CREDENTIALS_PATH:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(settings.GOOGLE_APPLICATION_CREDENTIALS_PATH)
    
    print(f"🔍 Checking available models in project: {settings.GOOGLE_CLOUD_PROJECT}...")
    
    try:
        aiplatform.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
        # In Vertex AI, we check the GenerativeModel list or the Model list
        from vertexai.generative_models import GenerativeModel
        
        # We can't easily list generative models via a simple call in some SDK versions, 
        # so let's try a very basic one like 'gemini-pro'
        
        test_model_name = "gemini-1.0-pro"
        print(f"🔄 Attempting to reach fallback model: {test_model_name}")
        
        # Test if we can at least initialize a model
        model = GenerativeModel(test_model_name)
        # We won't generate, just see if it errors on init (it usually doesn't, error happens on call)
        
        print("💡 Tip: A 404 often means you need to enable the 'Generative AI' feature.")
        print("Please visit: https://console.cloud.google.com/vertex-ai/generative/multimodal/create/text")
        print("Click 'Enable' if prompted.")

    except Exception as e:
        print(f"❌ Error during model check: {e}")

if __name__ == "__main__":
    asyncio.run(list_available_models())
