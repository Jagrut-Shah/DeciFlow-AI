import logging
# import vertexai
# from vertexai.generative_models import GenerativeModel
from app.domain.interfaces.llm_interface import ILLMService
from app.infrastructure.ai.models import LLMConfig, NormalizedLLMResponse
from app.infrastructure.ai.retry_wrapper import with_retry

logger = logging.getLogger(__name__)

class GeminiService(ILLMService):
    def __init__(self, project_id: str = "placeholder_project", location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        # vertexai.init(project=project_id, location=location)

    async def _execute_call(self, prompt: str, config: LLMConfig) -> NormalizedLLMResponse:
        # Mocking actual API call to Vertex AI for architectural stability without keys
        # In prod:
        # model = GenerativeModel(config.model_name)
        # response = await model.generate_content_async(prompt, generation_config={"temperature": config.temperature})
        
        logger.info(f"Mocking Vertex AI call to {config.model_name}...")
        import asyncio
        await asyncio.sleep(0.5) # Simulate network io
        
        # Simulating generic occasional failures for retry demonstration
        import random
        if random.random() < 0.2:
            raise ConnectionError("Simulated random Vertex connection drop")
            
        return NormalizedLLMResponse(
            content=f"Processed by {config.model_name}. Context: {prompt[:30]}...",
            tokens_used=145,
            finish_reason="STOP",
            raw_response={"mock": "data"}
        )

    async def generate_response(self, prompt: str, config: LLMConfig) -> NormalizedLLMResponse:
        logger.info(f"Executing Gemini Service generation. Config: temp={config.temperature}")
        return await with_retry(
            self._execute_call,
            prompt=prompt,
            config=config,
            max_retries=3,
            base_delay=1.0,
            timeout=10.0
        )
