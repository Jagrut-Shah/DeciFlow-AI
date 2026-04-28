import logging
from app.domain.interfaces.llm_interface import ILLMService
from app.infrastructure.ai.models import LLMConfig, NormalizedLLMResponse
from app.infrastructure.llm.vertex_adapter import VertexAdapter

logger = logging.getLogger(__name__)

class GeminiService(ILLMService):
    def __init__(self, project_id: str = None, location: str = None):
        self.adapter = VertexAdapter()

    async def generate_response(self, prompt: str, config: LLMConfig) -> NormalizedLLMResponse:
        logger.info(f"Executing Gemini Service generation via VertexAdapter. Model: {config.model_name}")
        
        # Mapping LLMConfig to adapter parameters
        model_type = "pro" if "pro" in config.model_name.lower() else "flash"
        
        response_text = await self.adapter.generate_content(
            prompt=prompt,
            model_type=model_type,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        
        if not response_text:
            return None

        return NormalizedLLMResponse(
            content=response_text,
            tokens_used=0, # Adapter doesn't currently return token count
            finish_reason="STOP",
            raw_response={"source": "VertexAdapter"}
        )
