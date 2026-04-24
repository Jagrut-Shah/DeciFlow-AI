import logging
import os
import asyncio
from typing import Optional, List, Dict
from app.core.config import settings

# Try to import both SDKs
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel as VertexModel
    HAS_VERTEX = True
except ImportError:
    HAS_VERTEX = False

try:
    from google import genai
    from google.genai import types as gen_types
    HAS_GOOGLE_AI = True
except ImportError:
    HAS_GOOGLE_AI = False

logger = logging.getLogger(__name__)

class VertexAdapter:
    """
    Hybrid Adapter for Gemini (Vertex AI or Google GenAI SDK).
    Prioritizes API Key (Google GenAI) if provided, otherwise falls back to Vertex AI.
    """
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.project = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self._mode = "google_ai" if self.api_key else "vertex"
        self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS_PATH
        self._client = None
        self._initialized = False

        if self._mode == "vertex" and settings.GOOGLE_APPLICATION_CREDENTIALS_PATH:
            # Setup Vertex credentials
            path = settings.GOOGLE_APPLICATION_CREDENTIALS_PATH
            # If path is relative, try to resolve it from current dir OR one level up (project root)
            if not os.path.isabs(path):
                if os.path.exists(path):
                    abs_path = os.path.abspath(path)
                else:
                    # Try one level up (common if running from backend/ folder)
                    parent_path = os.path.join("..", path)
                    if os.path.exists(parent_path):
                        abs_path = os.path.abspath(parent_path)
                    else:
                        abs_path = path # Fallback to original
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_path
            else:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

    def _ensure_init(self):
        if self._initialized:
            return

        if not HAS_GOOGLE_AI:
            raise ImportError("google-genai package not installed. Run: pip install google-genai")

        try:
            if self.api_key:
                # Mode: Google AI (API Key)
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Gemini via Google AI SDK (API Key)")
            else:
                # Mode: Vertex AI (Service Account)
                # Ensure the environment variable is set for the SDK to find the credentials
                if self.credentials_path:
                    # Resolve path relative to project root (backend/app/infrastructure/llm/ -> backend/app/infrastructure/ -> backend/app/ -> backend/ -> root/)
                    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
                    abs_cred_path = os.path.abspath(os.path.join(root_dir, self.credentials_path))
                    if os.path.exists(abs_cred_path):
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_cred_path
                        logger.info(f"Set GOOGLE_APPLICATION_CREDENTIALS to {abs_cred_path}")
                    else:
                        logger.warning(f"Credentials file not found at {abs_cred_path}")

                self._client = genai.Client(
                    vertexai=True,
                    project=self.project,
                    location=self.location
                )
                logger.info(f"Initialized Gemini via Vertex AI SDK (Project: {self.project}, Location: {self.location})")
            
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Client: {str(e)}", exc_info=True)
            raise

    async def generate_content(
        self, 
        prompt: str, 
        model_type: str = "flash",
        temperature: float = 0.2,
        max_tokens: int = 1000
    ) -> Optional[str]:
        """
        Generic content generation using Gemini via google-genai SDK.
        """
        try:
            self._ensure_init()
            model_name = settings.GEMINI_MODELS.get(model_type, settings.GEMINI_MODELS["flash"])
            
            # The new SDK is async-friendly via asyncio.to_thread for now as the sync client is robust
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=model_name,
                contents=prompt,
                config=gen_types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text

        except Exception as e:
            mode_str = "google_ai" if self.api_key else "vertex"
            logger.error(f"Gemini Generation Error ({mode_str} - {model_type}): {str(e)}", exc_info=True)
            return None

    async def generate_structured_insight(self, data: Dict) -> Optional[str]:
        """
        Specialized helper for InsightAgent to create narratives from structured metrics.
        """
        prompt = f"""
        You are a senior business analyst for DeciFlow AI.
        Analyze the following structured metrics and provide a concise, high-impact narrative summary (2-3 sentences).
        Focus on identifying the 'story' behind the numbers.
        
        DATA:
        {data}
        
        SUMMARY:
        """
        return await self.generate_content(prompt, model_type="flash")

    async def generate_strategic_advice(self, insights: List[Dict]) -> Optional[str]:
        """
        Specialized helper for DecisionAgent to provide creative strategic advisory.
        """
        prompt = f"""
        You are a Chief Strategy Officer. 
        Given the following business insights, provide one creative and actionable strategic recommendation.
        Don't just repeat the insights; offer a proactive move.
        
        INSIGHTS:
        {insights}
        
        STRATEGY:
        """
        return await self.generate_content(prompt, model_type="pro", temperature=0.7)
