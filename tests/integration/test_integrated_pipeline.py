import requests
import os
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_execute_from_file():
    print("--- Testing /pipeline/execute-from-file ---")
    # Point to the data folder relative to this test file
    file_path = os.path.join(os.path.dirname(__file__), "../data/sample_pipeline_data.csv")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, 'rb') as f:
        files = {'file': ('sample.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/pipeline/execute-from-file", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    try:
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if response.status_code == 200:
            print("\nPipeline execution successful!")
            # Check for simulation results in the output
            if "simulation" in result.get("data", {}).get("stages", {}):
                print("Simulation stage confirmed in output.")
            else:
                print("Warning: Simulation stage NOT found in output.")
        else:
            print(f"\nPipeline failed: {result.get('message')}")
            
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(response.text)

if __name__ == "__main__":
    test_execute_from_file()
