from abc import ABC, abstractmethod
from typing import Any, Dict

class IFeatureService(ABC):
    @abstractmethod
    async def extract_features(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        ...
