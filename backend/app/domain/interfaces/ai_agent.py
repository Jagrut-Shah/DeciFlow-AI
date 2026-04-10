from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAIAgent(ABC):
    """
    Abstract Base Class for AI Agents.
    The AI team will inherit from this to implement specific agents,
    ensuring they conform to the backend's expected interface.
    """
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes in a contextual dictionary and returns the agent's output.
        """
        ...
