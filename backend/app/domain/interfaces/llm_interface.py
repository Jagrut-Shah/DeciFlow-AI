from abc import ABC, abstractmethod
from app.infrastructure.ai.models import LLMConfig, NormalizedLLMResponse

class ILLMService(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, config: LLMConfig) -> NormalizedLLMResponse:
        ...
