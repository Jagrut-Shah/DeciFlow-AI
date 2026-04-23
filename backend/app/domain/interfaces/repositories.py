from abc import ABC, abstractmethod
from typing import Any, Dict

class IUserRepository(ABC):
    @abstractmethod
    def load_user(self, user_id: str) -> Dict[str, Any]: ...
    
    @abstractmethod
    def store_user(self, user_data: Dict[str, Any]) -> bool: ...

class IDatasetRepository(ABC):
    @abstractmethod
    def load_data(self, source_path: str) -> Any: ...
    
    @abstractmethod
    def store_data(self, destination_path: str, data: Any) -> bool: ...

class IMetricsRepository(ABC):
    @abstractmethod
    def load_metrics(self, metric_id: str) -> Dict[str, Any]: ...
    
    @abstractmethod
    def store_metrics(self, metric_data: Dict[str, Any]) -> bool: ...
