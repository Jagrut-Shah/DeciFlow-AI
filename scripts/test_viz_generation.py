import asyncio
import os
import sys
from typing import Dict

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import logging
logging.basicConfig(level=logging.INFO)

from app.infrastructure.llm.vertex_adapter import VertexAdapter
from app.core.config import settings

async def test_viz_generation():
    print("Testing Dynamic Visualization Generation...")
    
    adapter = VertexAdapter()
    
    # Mock data - Inventory
    metrics = {
        "total_stock": 5000,
        "out_of_stock_items": 12,
        "reorder_points_hit": 45
    }
    
    categories = {
        "Warehouse A": {"stock": 3000, "total_revenue": 0},
        "Warehouse B": {"stock": 1500, "total_revenue": 0},
        "Warehouse C": {"stock": 500, "total_revenue": 0}
    }
    
    print("\nRequesting visualization from Gemini...")
    viz_config = await adapter.generate_visualization_config(metrics, categories)
    
    print("\n--- Visualization Config ---")
    import json
    print(json.dumps(viz_config, indent=2))
    
    with open("last_viz_config.json", "w") as f:
        json.dump(viz_config, f, indent=2)
    
    assert "type" in viz_config
    assert "data" in viz_config
    assert "title" in viz_config
    print("\nSuccess! Visualization config generated.")

if __name__ == "__main__":
    asyncio.run(test_viz_generation())
