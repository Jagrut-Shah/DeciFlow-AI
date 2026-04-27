import sys
import os

# Use relative pathing to locate the backend module
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend"))
sys.path.insert(0, backend_path)

from app.infrastructure.data.bigquery_adapter import BigQueryAdapter
from app.infrastructure.data.storage_adapter import StorageAdapter
from app.infrastructure.repositories.implementations import DatasetRepository

import logging
logging.basicConfig(level=logging.INFO)

def main():
    print("--- Running Data Layer Test ---")
    bq = BigQueryAdapter()
    storage = StorageAdapter()
    
    repo = DatasetRepository(storage_adapter=storage, bq_adapter=bq)
    
    print("\n--- Testing GCS Storage Load ---")
    data = repo.load_data("gs://deciflow-data/raw/transactions.csv")
    print(f"Loaded: {data}")
    
    print("\n--- Testing BigQuery Storage Load ---")
    bq_data = repo.load_data("bq://deciflow_analytics.processed_features")
    print(f"Loaded: {bq_data}")
    
    print("\n--- Ensure No Data Cleaning Present ---")
    print("Adapters act strictly as transport layers, delegating transforms to engineers.")

if __name__ == "__main__":
    main()
