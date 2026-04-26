from abc import ABC, abstractmethod
from typing import Any, Dict

class IDataService(ABC):
    @abstractmethod
    async def process_raw_data(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    def parse_csv_content(self, content: bytes) -> Dict[str, Any]:
        ...

    @abstractmethod
    def parse_json_content(self, content: bytes) -> Dict[str, Any]:
        ...
