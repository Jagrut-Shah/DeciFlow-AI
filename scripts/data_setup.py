import os

base_dir = r"c:\Users\HP\Downloads\DeciFlow AI\backend\app"
infra_data_dir = os.path.join(base_dir, "infrastructure", "data")
infra_repo_dir = os.path.join(base_dir, "infrastructure", "repositories")
os.makedirs(infra_data_dir, exist_ok=True)
os.makedirs(infra_repo_dir, exist_ok=True)

# 1. INTERFACES
repos_interface_code = """from abc import ABC, abstractmethod
from typing import Any, Dict

class IUserRepository(ABC):
    @abstractmethod
    def load_user(self, user_id: str) -> Dict[str, Any]: pass
    
    @abstractmethod
    def store_user(self, user_data: Dict[str, Any]) -> bool: pass

class IDatasetRepository(ABC):
    @abstractmethod
    def load_data(self, source_path: str) -> Any: pass
    
    @abstractmethod
    def store_data(self, destination_path: str, data: Any) -> bool: pass

class IMetricsRepository(ABC):
    @abstractmethod
    def load_metrics(self, metric_id: str) -> Dict[str, Any]: pass
    
    @abstractmethod
    def store_metrics(self, metric_data: Dict[str, Any]) -> bool: pass
"""
with open(os.path.join(base_dir, "domain", "interfaces", "repositories.py"), "w", encoding="utf-8") as f: f.write(repos_interface_code)

# 2. ADAPTERS
bq_code = """import logging
from typing import Any, List, Dict

logger = logging.getLogger(__name__)

class BigQueryAdapter:
    def __init__(self, project_id: str = "default-project"):
        self.project_id = project_id
        
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"BigQueryAdapter: Executing query on {self.project_id}")
        # Placeholder for actual google.cloud.bigquery Client logic
        return [{"mock_id": "123", "result": "mock_data"}]
        
    def insert_rows(self, table_id: str, rows: List[Dict[str, Any]]) -> bool:
        logger.info(f"BigQueryAdapter: Inserting {len(rows)} rows into {table_id}")
        return True
"""
with open(os.path.join(infra_data_dir, "bigquery_adapter.py"), "w", encoding="utf-8") as f: f.write(bq_code)

storage_code = """import logging
from typing import Any

logger = logging.getLogger(__name__)

class StorageAdapter:
    def __init__(self, bucket_name: str = "default-bucket"):
        self.bucket_name = bucket_name
        
    def read_blob(self, blob_name: str) -> str:
        logger.info(f"StorageAdapter: Reading blob {blob_name} from {self.bucket_name}")
        # Placeholder for actual google.cloud.storage Blob logic
        return "mock_blob_contents_structured_as_csv"
        
    def write_blob(self, blob_name: str, data: Any) -> bool:
        logger.info(f"StorageAdapter: Writing blob {blob_name} to {self.bucket_name}")
        return True
"""
with open(os.path.join(infra_data_dir, "storage_adapter.py"), "w", encoding="utf-8") as f: f.write(storage_code)
with open(os.path.join(infra_data_dir, "__init__.py"), "w", encoding="utf-8") as f: f.write("")

# 3. REPOSITORIES
repo_impl_code = """from typing import Any, Dict
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
"""
with open(os.path.join(infra_repo_dir, "implementations.py"), "w", encoding="utf-8") as f: f.write(repo_impl_code)
with open(os.path.join(infra_repo_dir, "__init__.py"), "w", encoding="utf-8") as f: f.write("")

print("Data infrastructure generation complete.")
