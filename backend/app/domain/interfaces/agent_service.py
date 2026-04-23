from abc import ABC, abstractmethod
from typing import Any, Dict

class IAgentService(ABC):
    @abstractmethod
    async def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        ...
