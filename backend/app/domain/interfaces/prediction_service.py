from abc import ABC, abstractmethod
from typing import Any, Dict

class IPredictionService(ABC):
    @abstractmethod
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        ...
