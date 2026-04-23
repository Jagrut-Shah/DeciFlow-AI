from typing import Any, Dict
from app.domain.interfaces.repositories import IUserRepository, IDatasetRepository, IMetricsRepository
from app.infrastructure.data.bigquery_adapter import BigQueryAdapter
from app.infrastructure.data.storage_adapter import StorageAdapter

class UserRepository(IUserRepository):
    def __init__(self, db_adapter: BigQueryAdapter):
        self.db = db_adapter
        
    def load_user(self, user_id: str) -> Dict[str, Any]:
        query = f"SELECT * FROM Users WHERE id = '{user_id}' LIMIT 1;"
        results = self.db.execute_query(query)
        return results[0] if results else {}
        
    def store_user(self, user_data: Dict[str, Any]) -> bool:
        return self.db.insert_rows("Users", [user_data])

class DatasetRepository(IDatasetRepository):
    def __init__(self, storage_adapter: StorageAdapter, bq_adapter: BigQueryAdapter):
        # Utilizes storage for raw files and bq for structured schemas
        self.storage = storage_adapter
        self.bq = bq_adapter
        
    def load_data(self, source_path: str) -> Any:
        # STRICT RULE: WE DO NOT CLEAN DATA HERE! 
        # Just pure transport bytes/struct fetching.
        if source_path.startswith("bq://"):
            table_name = source_path.replace("bq://", "")
            return self.bq.execute_query(f"SELECT * FROM {table_name}")
        else:
            return self.storage.read_blob(source_path)
            
    def store_data(self, destination_path: str, data: Any) -> bool:
        if destination_path.startswith("bq://"):
            table_name = destination_path.replace("bq://", "")
            if isinstance(data, list):
                return self.bq.insert_rows(table_name, data)
            return False
        else:
            return self.storage.write_blob(destination_path, data)

class MetricsRepository(IMetricsRepository):
    def __init__(self, db_adapter: BigQueryAdapter):
        self.db = db_adapter
        
    def load_metrics(self, metric_id: str) -> Dict[str, Any]:
        results = self.db.execute_query(f"SELECT * FROM Telemetry WHERE id='{metric_id}'")
        return results[0] if results else {}
        
    def store_metrics(self, metric_data: Dict[str, Any]) -> bool:
        return self.db.insert_rows("Telemetry", [metric_data])
