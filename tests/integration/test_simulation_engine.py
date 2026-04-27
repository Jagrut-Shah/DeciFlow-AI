import sys
import os
import time

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend"))
sys.path.append(backend_path)

from app.services.simulation_service import SimulationService

def test_simulation_engine():
    print("--- Running Simulation Engine Independent Test ---")
    service = SimulationService()
    
    # Test cases: (Input Decision, Expected Risk)
    test_cases = [
        ({"score": 0.9, "confidence": 0.85, "action": "EXPAND_MARKET"}, "low"),
        ({"score": 0.7, "confidence": 0.6, "action": "MAINTAIN_BUDGET"}, "medium"),
        ({"score": 0.4, "confidence": 0.3, "action": "REDUCE_OPERATIONS"}, "high"),
        (None, "unknown") # Fallback case
    ]
    
    all_results = []
    
    start_time = time.time()
    
    for decision, expected_risk in test_cases:
        print(f"\nTesting Action: {decision.get('action') if decision else 'None'}")
        result = service.simulate(decision)
        
        # Validation
        assert result["risk_level"] == expected_risk
        if decision:
            assert result["projected_roi"] >= 0.8 # Minimum ROI per logic
            assert "recommendation" in result
            print(f"  Result: ROI={result['projected_roi']}, Risk={result['risk_level']}")
        else:
            assert result["_fallback"] is True
            print("  Result: Fallback triggered as expected.")
        
        all_results.append(result)
    
    end_time = time.time()
    execution_time = (end_time - start_time) * 1000 # in ms
    
    print(f"\n--- Simulation Engine Test Passed ---")
    print(f"Total Execution Time: {execution_time:.2f}ms")
    
    return all_results, execution_time

if __name__ == "__main__":
    try:
        results, duration = test_simulation_engine()
        # The user wants specific output format
        print("\n[FINAL_OUTPUT]")
        import json
        print(json.dumps({
            "simulation_results": results,
            "execution_time": f"{duration:.2f}ms",
            "errors": None
        }, indent=2))
    except Exception as e:
        print(f"\n[FINAL_OUTPUT]")
        print(f"errors: {str(e)}")
        sys.exit(1)
