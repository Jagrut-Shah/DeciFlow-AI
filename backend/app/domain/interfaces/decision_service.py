from abc import ABC, abstractmethod
from typing import Any, Dict

class IDecisionService(ABC):
    @abstractmethod
    def orchestrate_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ...
