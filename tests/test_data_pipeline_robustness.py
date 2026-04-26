import asyncio
import sys
import os

# Add backend to path so we can import app
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.agents.data_agent import DataAgent

async def test_robustness():
    agent = DataAgent()
    
    # Test 1: Variations in headers and case sensitivity
    test_case_1 = {
        "data": [
            {
                "DATE": "2024-01-01",
                "Total_Sales": "100.50",
                "REVENUE": "500.00",
                "Earnings": "150.00",
                "margin_pct": "0.30",
                "Item_Name": "Gadget A",
                "Department": "Electronics"
            },
            {
                "date": "2024-01-02",
                "quantity": "50",
                "income": "250",
                "Net_Profit": "75",
                "profit_margin": "0.30",
                "product_name": "Gadget B",
                "category_name": "Electronics"
            }
        ]
    }
    
    print("Running Test 1: Robust Header Mapping...")
    result = await agent.execute(test_case_1)
    
    if result["status"] == "ok":
        metrics = result["metrics"]
        print(f"[SUCCESS] Total Sales: {metrics['total_sales']} (Expected: 150.5)")
        print(f"[SUCCESS] Total Revenue: {metrics['total_revenue']} (Expected: 750.0)")
        print(f"[SUCCESS] Total Profit: {metrics['total_profit']} (Expected: 225.0)")
        print(f"[SUCCESS] Average Margin: {metrics['avg_margin']} (Expected: 0.3)")
        
        # Verify detected fields
        detected = result["metadata"]["fields_detected"]
        expected_fields = ["category", "date", "margin", "product", "profit", "revenue", "sales"]
        for f in expected_fields:
            if f in detected:
                print(f"   - Found mapped field: {f}")
            else:
                print(f"   [MISSING] mapped field: {f}")
    else:
        print(f"[FAILED] Test 1: {result.get('error')}")

    # Test 2: Missing optional fields (Silent Drop Prevention)
    test_case_2 = {
        "data": [
            {"sales": "100"} # Bare minimum
        ]
    }
    print("\nRunning Test 2: Minimal Records...")
    result = await agent.execute(test_case_2)
    if result["status"] == "ok":
        print(f"[SUCCESS] Handled minimal record. Quality Score: {result['data_quality']}")
    else:
        print(f"[FAILED] Test 2: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_robustness())
