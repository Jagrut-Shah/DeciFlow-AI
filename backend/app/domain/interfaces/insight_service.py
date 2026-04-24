from abc import ABC, abstractmethod
from typing import Any, Dict

class IInsightService(ABC):
    @abstractmethod
    async def generate_insights(self, features: Dict[str, Any]) -> Dict[str, Any]:
        ...
