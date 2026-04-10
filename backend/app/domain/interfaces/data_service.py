from abc import ABC, abstractmethod
from typing import Any, Dict

class IDataService(ABC):
    @abstractmethod
    def process_raw_data(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...
