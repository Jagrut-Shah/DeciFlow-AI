from abc import ABC, abstractmethod
from typing import Any, Dict

class ISimulationService(ABC):
    @abstractmethod
    async def simulate(self, session_id: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        ...
