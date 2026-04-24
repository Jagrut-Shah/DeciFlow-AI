import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

async def test_vertex_connectivity():
    print("🚀 Initializing Vertex AI Connectivity Test...")
    
    try:
        from app.infrastructure.llm.vertex_adapter import VertexAdapter
        from app.core.config import settings
        
        # Initialize Adapter
        adapter = VertexAdapter()
        
        if settings.GOOGLE_API_KEY:
            print(f"🔑 Authentication Mode: Google AI (API Key)")
        else:
            print(f"☁️ Authentication Mode: Vertex AI (Service Account)")
            print(f"📍 Project: {settings.GOOGLE_CLOUD_PROJECT}")
            print(f"📍 Location: {settings.GOOGLE_CLOUD_LOCATION}")

        if not settings.GOOGLE_API_KEY and settings.GOOGLE_CLOUD_PROJECT == "your-project-id":
            print("⚠️ Skipping active API call: Project ID is still default and no API Key found.")
            return

        print("🔗 Testing narrative generation...")
        metrics = {"total_sales": 50000, "conversion_rate": 0.05}
        narrative = None
        try:
            narrative = await adapter.generate_structured_insight(metrics)
        except Exception as e:
            print(f"❌ Actual Error: {e}")
        
        if narrative:
            print(f"✅ Success! AI Narrative: {narrative[:100]}...")
        else:
            print("❌ Failed: Empty response or Error occurred.")
            
    except ImportError as e:
        print(f"❌ Error: Missing dependencies. Did you run 'pip install -r requirements.txt'? ({e})")
    except Exception as e:
        print(f"❌ unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_vertex_connectivity())
