import os

base_dir = r"c:\Users\HP\Downloads\DeciFlow AI\backend\app"
infra_ai_dir = os.path.join(base_dir, "infrastructure", "ai")
os.makedirs(infra_ai_dir, exist_ok=True)
os.makedirs(os.path.join(base_dir, "domain", "interfaces"), exist_ok=True)

# 1. Models
models_code = """from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class LLMConfig(BaseModel):
    model_name: str = "gemini-1.5-pro"
    temperature: float = 0.2
    max_tokens: int = 1024
    top_p: float = 0.95

class NormalizedLLMResponse(BaseModel):
    content: str
    tokens_used: int
    finish_reason: str
    raw_response: Any = Field(exclude=True, repr=False)
"""
with open(os.path.join(infra_ai_dir, "models.py"), "w", encoding="utf-8") as f: f.write(models_code)
with open(os.path.join(infra_ai_dir, "__init__.py"), "w", encoding="utf-8") as f: f.write("")

# 2. Interface
llm_interface_code = """from abc import ABC, abstractmethod
from app.infrastructure.ai.models import LLMConfig, NormalizedLLMResponse

class ILLMService(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, config: LLMConfig) -> NormalizedLLMResponse:
        pass
"""
with open(os.path.join(base_dir, "domain", "interfaces", "llm_interface.py"), "w", encoding="utf-8") as f: f.write(llm_interface_code)

# 3. Templates
templates_code = """import re

class PromptTemplate:
    def __init__(self, template: str):
        self.template = template
        self.variables = set(re.findall(r"\{(\w+)\}", template))

    def format(self, **kwargs) -> str:
        missing = self.variables - kwargs.keys()
        if missing:
            raise ValueError(f"Missing prompt variables: {missing}")
        return self.template.format(**kwargs)
"""
with open(os.path.join(infra_ai_dir, "templates.py"), "w", encoding="utf-8") as f: f.write(templates_code)

# 4. Retry Wrapper
retry_code = """import asyncio
import logging
import time
from typing import Callable, Coroutine, Any

logger = logging.getLogger(__name__)

async def with_retry(
    func: Callable[..., Coroutine[Any, Any, Any]],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    timeout: float = 30.0,
    **kwargs
) -> Any:
    for attempt in range(1, max_retries + 1):
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Attempt {attempt} timed out after {timeout}s.")
        except Exception as e:
            logger.warning(f"Attempt {attempt} failed: {str(e)}")
            
        if attempt == max_retries:
            logger.error(f"All {max_retries} attempts failed.")
            raise Exception("LLM interaction failed after max retries")
            
        delay = base_delay * (2 ** (attempt - 1))
        logger.info(f"Retrying in {delay}s...")
        await asyncio.sleep(delay)
"""
with open(os.path.join(infra_ai_dir, "retry_wrapper.py"), "w", encoding="utf-8") as f: f.write(retry_code)

# 5. Gemini / Vertex Implementation
vertex_code = """import logging
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
"""
with open(os.path.join(infra_ai_dir, "vertex_ai.py"), "w", encoding="utf-8") as f: f.write(vertex_code)

print("AI Integration structure generated.")
