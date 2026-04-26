import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.infrastructure.llm.vertex_adapter import VertexAdapter
from app.core.config import settings

async def main():
    print("--- DeciFlow AI - Vertex AI Adapter Test ---")
    
    # Mock settings if needed
    if not settings.GOOGLE_API_KEY and settings.GOOGLE_CLOUD_PROJECT == "your-project-id":
        print("Warning: Vertex AI / Google GenAI not configured in settings.")
        print("This test will likely fail or skip.")
    
    adapter = VertexAdapter()
    
    # 1. Test Generic Content Generation
    print("\nTesting: Generic Content Generation...")
    result = await adapter.generate_content("Hello Gemini, say 'Operational Ready'")
    if result:
        print(f"Result: {result}")
    else:
        print("Result: FAILED")

    # 2. Test Insight Narrative
    print("\nTesting: Insight Narrative Generation...")
    mock_metrics = {
        "total_revenue": 50000,
        "trend": "increasing",
        "avg_order_value": 150
    }
    narrative = await adapter.generate_structured_insight(mock_metrics)
    if narrative:
        print(f"Narrative: {narrative}")
    else:
        print("Narrative: FAILED")

    # 3. Test Strategic Advice
    print("\nTesting: Strategic Advice Generation...")
    mock_insights = [
        {"text": "Weekend sales are booming", "priority": "high", "impact": "positive"}
    ]
    advice = await adapter.generate_strategic_advice(mock_insights)
    if advice:
        print(f"Strategy: {advice}")
    else:
        print("Strategy: FAILED")

if __name__ == "__main__":
    asyncio.run(main())
