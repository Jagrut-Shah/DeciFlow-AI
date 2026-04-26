import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(r"c:\Users\HP\Downloads\DeciFlow AI\backend"))

from app.services.data_service import DataService

def test_parsing_logic():
    ds = DataService()
    
    # Test CSV parsing
    csv_data = b"id,name,value\n1,test,100\n2,example,200"
    parsed_csv = ds.parse_csv_content(csv_data)
    print(f"Parsed CSV Record Count: {len(parsed_csv['data'])}")
    print(f"First Record: {parsed_csv['data'][0]}")
    assert len(parsed_csv['data']) == 2
    assert parsed_csv['data'][0]['name'] == 'test'
    
    # Test JSON parsing
    json_data = b'{"data": [{"id": 1, "name": "test_json"}]}'
    parsed_json = ds.parse_json_content(json_data)
    print(f"Parsed JSON Record Count: {len(parsed_json['data'])}")
    print(f"First Record: {parsed_json['data'][0]}")
    assert len(parsed_json['data']) == 1
    assert parsed_json['data'][0]['name'] == 'test_json'
    
    print("\nParsing logic verification successful!")

if __name__ == "__main__":
    try:
        test_parsing_logic()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
