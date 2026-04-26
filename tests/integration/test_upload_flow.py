import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.path.abspath(r"c:\Users\HP\Downloads\DeciFlow AI\backend"))

from app.main import app

client = TestClient(app)

def test_upload_csv():
    """Test uploading a CSV file."""
    csv_content = "id,name,value\n1,test,100\n2,example,200\n3,data,300"
    files = {"file": ("test.csv", csv_content, "text/csv")}
    
    response = client.post("/api/v1/data/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["filename"] == "test.csv"
    assert data["record_count"] == 3
    assert len(data["preview"]) == 3
    assert data["preview"][0]["name"] == "test"

def test_upload_json():
    """Test uploading a JSON file."""
    json_content = '{"data": [{"id": 1, "name": "test"}, {"id": 2, "name": "example"}]}'
    files = {"file": ("test.json", json_content, "application/json")}
    
    response = client.post("/api/v1/data/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["record_count"] == 2
    assert data["preview"][0]["name"] == "test"

def test_upload_invalid_type():
    """Test uploading an unsupported file type."""
    files = {"file": ("test.txt", "some text", "text/plain")}
    
    response = client.post("/api/v1/data/upload", files=files)
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

if __name__ == "__main__":
    # Run tests manually if script is executed directly
    print("--- Running Upload Flow Integration Tests ---")
    try:
        test_upload_csv()
        print("[SUCCESS] CSV Upload Test")
        test_upload_json()
        print("[SUCCESS] JSON Upload Test")
        test_upload_invalid_type()
        print("[SUCCESS] Invalid Type Test")
        print("\nAll tests passed!")
    except Exception as e:
        print(f"[FAILURE] Tests failed: {e}")
        sys.exit(1)
