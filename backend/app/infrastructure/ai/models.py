from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class LLMConfig(BaseModel):
    model_name: str = "gemini-2.5-pro"
    temperature: float = 0.2
    max_tokens: int = 1024
    top_p: float = 0.95

class NormalizedLLMResponse(BaseModel):
    content: str
    tokens_used: int
    finish_reason: str
    raw_response: Any = Field(exclude=True, repr=False)
