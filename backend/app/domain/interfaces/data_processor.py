from abc import ABC, abstractmethod
from typing import Any, List

class BaseDataProcessor(ABC):
    """
    Abstract Base Class for Data Processing.
    The Data/ML team will implement this to handle data ingestion,
    preprocessing, and transformation.
    """
    @abstractmethod
    def ingest(self, raw_data: Any) -> Any:
        ...

    @abstractmethod
    def transform(self, data: Any) -> List[Any]:
        ...
