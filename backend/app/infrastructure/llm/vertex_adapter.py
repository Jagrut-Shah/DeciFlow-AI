import logging
import os
import asyncio
import time
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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

# Shared state for singleton client management
_shared_client = None
_init_lock = asyncio.Lock()

class VisualizationConfig(BaseModel):
    """Schema for AI-generated visualization configurations."""
    type: str
    title: str
    data: List[Dict]
    description: str

class VertexAdapter:
    """
    Hybrid Adapter for Gemini (Vertex AI or Google GenAI SDK).
    Prioritizes API Key (Google GenAI) if provided, otherwise falls back to Vertex AI.
    """
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.project = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS_PATH
        
        # Priority: Vertex AI (Service Account) if path is provided AND file exists,
        # otherwise Google AI (API Key)
        self._mode = "google_ai" # Default to API Key
        
        if self.credentials_path:
            # Resolve path to check existence
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            abs_cred_path = os.path.abspath(os.path.join(root_dir, self.credentials_path))
            
            if os.path.exists(abs_cred_path) or os.path.exists(self.credentials_path):
                self._mode = "vertex"
            else:
                logger.warning(f"VertexAdapter: Service account file not found. Falling back to Google AI (API Key). Checked: {abs_cred_path}")
        
        if self._mode == "google_ai" and not self.api_key:
            logger.error("VertexAdapter: No credentials available (no Service Account and no API Key)")
            
        self._client = None
        self._initialized = False

        if self._mode == "vertex" and self.credentials_path:
            # Setup Vertex credentials
            path = self.credentials_path
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

    @property
    def is_available(self) -> bool:
        """Checks if the adapter has necessary credentials to operate."""
        return bool(self.api_key or self.credentials_path)

    async def _ensure_init(self):
        """
        Ensures the Gemini client is initialized in a thread-safe/async-safe way.
        Uses a global shared client to avoid repeated heavy initialization.
        """
        global _shared_client
        
        if _shared_client is not None:
            self._client = _shared_client
            self._initialized = True
            return

        async with _init_lock:
            # Double-check inside lock
            if _shared_client is not None:
                self._client = _shared_client
                self._initialized = True
                return

            if not HAS_GOOGLE_AI:
                raise ImportError("google-genai package not installed. Run: pip install google-genai")

            try:
                # NEW: Run synchronous client initialization in a thread to avoid blocking the loop
                _shared_client = await asyncio.to_thread(_create_client_sync, self)
                logger.info(f"Initialized Gemini Client (Mode: {self._mode})")
                
                self._client = _shared_client
                self._initialized = True
            except Exception as e:
                logger.error(f"VertexAdapter: Failed to initialize Gemini Client: {str(e)}", exc_info=True)
                raise

    async def generate_content(
        self,
        prompt: str,
        model_type: str = "flash",
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> Optional[str]:
        """
        Generates content from the LLM using the async client.
        """
        try:
            model_name = settings.GEMINI_MODELS.get(model_type, settings.GEMINI_MODELS["flash"])
            
            await self._ensure_init()
            if not self._client:
                logger.error(f"VertexAdapter: Client not initialized for {model_name}")
                return None

            # Dynamic timeout: Flash is faster than Pro
            actual_timeout = 30 if model_type == "flash" else (settings.TASK_TIMEOUT or 60)
            
            logger.debug(f"Starting async LLM call to {model_name} (Mode: {self._mode})...")
            start_time = time.time()

            # We use self._client.aio directly (it is an instance of AsyncClient)
            response = await asyncio.wait_for(
                self._client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=gen_types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                ),
                timeout=actual_timeout
            )
            
            latency = time.time() - start_time
            logger.info(f"LLM Success: {model_name} in {latency:.2f}s")
            
            if response:
                try:
                    if response.text:
                        return response.text
                except Exception as text_err:
                    logger.warning(f"LLM Response text extraction failed: {text_err}")
                    
                # Check for candidates and safety filters if text is missing
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason') and candidate.finish_reason == "SAFETY":
                        logger.warning(f"LLM Blocked: Safety filters triggered for {model_name}")
            
            logger.warning(f"LLM Empty: No valid text returned from {model_name}")
            return None

        except asyncio.TimeoutError:
            logger.error(f"LLM Timeout: {model_name} exceeded {actual_timeout}s")
            return None
        except Exception as e:
            # Enhanced error logging with more context
            error_msg = str(e)
            
            # Fallback for Gemini 2.5 models if they are not available in the region or have quota issues
            # 429 is quota, 404 is not found
            if "404" in error_msg or "not found" in error_msg.lower() or "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                fallback_model = "gemini-1.5-flash" if "flash" in model_type else "gemini-1.5-pro"
                logger.warning(f"LLM Model {model_name} failed ({error_msg}). Attempting fallback to {fallback_model}...")
                try:
                    # Use a slightly longer timeout for fallback to be safe
                    response = await asyncio.wait_for(
                        self._client.aio.models.generate_content(
                            model=fallback_model,
                            contents=prompt,
                            config=gen_types.GenerateContentConfig(
                                temperature=temperature,
                                max_output_tokens=max_tokens
                            )
                        ),
                        timeout=actual_timeout + 10
                    )
                    if response and response.text:
                        logger.info(f"LLM Fallback SUCCESS: {fallback_model} responded.")
                        return response.text
                except Exception as e2:
                    logger.error(f"LLM Fallback to {fallback_model} failed: {e2}")

            logger.error(
                f"LLM Failure ({model_name}): {error_msg}",
                exc_info=True,
                extra={
                    "model": model_name, 
                    "mode": self._mode,
                    "error_type": type(e).__name__
                }
            )
            return None

    async def generate_structured_insight(self, data: Dict) -> Optional[str]:
        """
        Specialized helper for InsightAgent to create narratives from structured metrics.
        """
        prompt = f"""
        You are a senior business analyst for DeciFlow AI.
        Analyze the following structured metrics and provide a concise, high-impact narrative summary (2-3 sentences).
        
        CRITICAL: Start the summary IMMEDIATELY with the core insight. DO NOT use introductory filler.
        
        DATA:
        {data}
        
        SUMMARY:
        """
        return await self.generate_content(prompt, model_type="flash")

    async def generate_insights_structured(self, metrics: Dict, categories: Dict) -> List[Dict]:
        """
        Generates a list of structured insights from business data using Gemini.
        """
        prompt = f"""
        Analyze this business data and provide a JSON list of 3-5 specific insights.
        Focus on trends, category performance, and any anomalies.
        
        METRICS: {metrics}
        CATEGORIES: {categories}
        
        RETURN JSON FORMAT ONLY:
        [
          {{
            "text": "Clear observation about the data",
            "priority": "high" | "medium" | "low",
            "impact": "positive" | "negative" | "neutral",
            "confidence": 0.0-1.0
          }}
        ]
        """
        try:
            response = await self.generate_content(prompt, model_type="flash", max_tokens=1000)
            if not response:
                return []
            
            return self._parse_json(response, expected_type=list)
        except Exception as e:
            logger.error(f"Failed to generate structured insights: {e}")
            return []

    async def generate_strategic_advice(self, insights: List[Dict]) -> Optional[str]:
        """
        Specialized helper for DecisionAgent to provide creative strategic advisory.
        """
        prompt = f"""
        You are a Chief Strategy Officer. 
        Given the following business insights, provide one creative and actionable strategic recommendation.
        
        INSIGHTS:
        {insights}
        
        STRATEGY:
        """
        return await self.generate_content(prompt, model_type="flash", temperature=0.7)

    async def generate_decision_package(self, insights: List[Dict], predictions: List[Dict]) -> Dict:
        """
        Consolidates structured decisions and strategic advice into a single AI call.
        """
        prompt = f"""
        You are a Chief Decision Officer and Strategy Lead.
        Based on these business insights and performance predictions, provide both structured actions and long-term strategic advice.
        
        INSIGHTS: {insights}
        PREDICTIONS: {predictions}
        
        RETURN JSON FORMAT ONLY:
        {{
          "decisions": [
            {{
              "action": "Specific actionable move",
              "type": "pricing" | "discount" | "category" | "strategy",
              "priority": "high" | "medium" | "low",
              "reason": "Data-backed reasoning",
              "expected_impact": "Impact with estimated percentage",
              "confidence": 0.0-1.0
            }}
          ],
          "advice": "The long-form strategic recommendation"
        }}
        """
        try:
            content_response = await self.generate_content(prompt, model_type="flash", max_tokens=1000)
            if not content_response:
                return {"decisions": [], "advice": "Strategic reasoning paused due to system signal."}
            
            pkg = self._parse_json(content_response, expected_type=dict)
            return {
                "decisions": pkg.get("decisions", []),
                "advice": pkg.get("advice") or "Strategy formulation complete."
            }
        except Exception as e:
            logger.error(f"Failed to generate decision package: {e}")
            return {"decisions": [], "advice": "Strategic reasoning paused due to system signal."}

    async def generate_visualization_config(self, metrics: Dict, categories: Dict) -> Dict:
        """
        Asks Gemini to decide on the best visualization for the given data.
        """
        prompt = f"""
        You are a Data Visualization Expert. Choose the single most impactful visualization.
        
        METRICS: {metrics}
        CATEGORIES: {categories}
        
        CHART TYPES AVAILABLE: "bar", "line", "area", "pie"
        
        RETURN JSON FORMAT ONLY:
        {{
          "type": "bar" | "line" | "area" | "pie",
          "title": "Clear Chart Title",
          "data": [
            {{ "name": "Category/Date", "value": 123.45 }}
          ],
          "description": "Short impactful observation."
        }}
        """
        try:
            content = await self.generate_content(prompt, model_type="flash", max_tokens=1000)
            if not content:
                return self._fallback_visualization(categories)
                
            return self._parse_json(content, expected_type=dict) or self._fallback_visualization(categories)
        except Exception as e:
            logger.error(f"Failed to generate visualization config: {e}")
            return self._fallback_visualization(categories)

    def _parse_json(self, text: str, expected_type: type = dict) -> Any:
        """Robust JSON extraction from LLM response."""
        import json
        import re
        try:
            # 1. Strip markdown code blocks
            cleaned = text.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            # 2. Extract the first valid JSON structure using regex (to handle trailing text)
            # Use non-greedy match to find the first complete block
            pattern = r'\[.*\]' if expected_type == list else r'\{.*\}'
            json_match = re.search(pattern, cleaned, re.DOTALL)
            
            if json_match:
                candidate = json_match.group(0)
                # 3. Final cleanup: remove trailing commas (common LLM error)
                candidate = re.sub(r',\s*([\]}])', r'\1', candidate)
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    # Try to fix unescaped newlines in strings
                    candidate = candidate.replace('\n', '\\n').replace('\r', '\\r')
                    return json.loads(candidate)
            
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"JSON Parse failed: {str(e)[:50]}. First 50 chars of input: {text[:50]}")
            return [] if expected_type == list else {}

    def _fallback_visualization(self, categories: Dict) -> Dict:
        """Safe fallback visualization if LLM fails."""
        data = []
        for name, stats in list(categories.items())[:5]:
            data.append({"name": name, "value": stats.get("total_revenue", 0)})
        
        return {
            "type": "bar",
            "title": "Top Categories by Revenue",
            "data": data,
            "description": "Comparison of performance across primary business categories."
        }

def _create_client_sync(adapter: 'VertexAdapter'):
    """Synchronous client creation for thread execution."""
    from google import genai
    
    # Priority 1: Vertex AI Mode (Service Account)
    if adapter._mode == "vertex":
        logger.info(f"Initializing Google GenAI Client in VERTEX mode (Project: {adapter.project})")
        return genai.Client(
            vertexai=True,
            project=adapter.project,
            location=adapter.location
        )
    
    # Priority 2: Google AI Mode (API Key)
    if adapter.api_key:
        logger.info("Initializing Google GenAI Client in GOOGLE_AI mode (API Key)")
        return genai.Client(api_key=adapter.api_key)
    
    # Fallback
    logger.warning("No credentials found, defaulting to Vertex AI initialization attempt")
    return genai.Client(
        vertexai=True,
        project=adapter.project,
        location=adapter.location
    )
