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
            logger.info(f"Gemini Finish Reason: {response.candidates[0].finish_reason}")
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
        
        CRITICAL: Start the summary IMMEDIATELY with the core insight. DO NOT use introductory filler like "Here is your summary" or "Based on the data".
        
        DATA:
        {data}
        
        SUMMARY:
        """
        return await self.generate_content(prompt, model_type="flash")

    async def generate_insights_structured(self, metrics: Dict, categories: Dict) -> List[Dict]:
        """
        Generates a list of structured insights from business data using Gemini.
        Returns a list of dicts: {"text": str, "priority": str, "impact": str, "confidence": float}
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
            
            # Robust JSON extraction
            import json
            import re
            
            # Look for JSON block within markdown if present
            cleaned = response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
                
            json_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            # Fallback to direct load if no markers but valid string
            try:
                return json.loads(cleaned)
            except:
                return []
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
        Don't just repeat the insights; offer a proactive move.
        
        INSIGHTS:
        {insights}
        
        STRATEGY:
        """
        return await self.generate_content(prompt, model_type="flash", temperature=0.7)

    async def generate_decision_package(self, insights: List[Dict], predictions: List[Dict]) -> Dict:
        """
        Consolidates structured decisions and strategic advice into a single AI call.
        Returns {"decisions": List[Dict], "advice": str}
        """
        prompt = f"""
        You are a Chief Decision Officer and Strategy Lead.
        Based on these business insights and performance predictions, provide both structured actions and long-term strategic advice.
        
        INSIGHTS: {insights}
        PREDICTIONS: {predictions}
        
        CRITICAL INSTRUCTIONS:
        1. DO NOT use generic phrases like "Analysis complete" or "Wait for data".
        2. DO NOT use introductory filler. Start with the strategic insight directly.
        3. Provide SPECIFIC strategic advice based on the metrics provided.
        4. Decisions MUST be actionable (e.g., "Launch loyalty program for Top Categories" instead of "Monitor").
        
        TASK 1: Provide 3 structured business decisions.
        TASK 2: Provide one creative, actionable strategic recommendation (advice).
        
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
          "advice": "The long-form strategic recommendation (minimum 2 sentences, highly specific)"
        }}
      
        """
    async def generate_content(
        self,
        prompt: str,
        model_type: str = "flash",
        temperature: float = 0.7
    ) -> str:
        try:
            # ✅ Initialize model if not already done
            if not hasattr(self, "model"):
                import vertexai
                from vertexai.generative_models import GenerativeModel

                vertexai.init(
                    project="bio-budget",
                    location="us-central1"
                )

                self.model = GenerativeModel("gemini-2.5-flash")

            # ✅ Generate response
            response = self.model.generate_content(prompt)

            print("RAW CHAT RESPONSE:", response)

            # ✅ Primary extraction
            if hasattr(response, "text") and response.text:
                return response.text

            # ✅ Fallback extraction
            if hasattr(response, "candidates") and response.candidates:
                return response.candidates[0].content.parts[0].text

            raise Exception("No valid response from Gemini")

        except Exception as e:
            print("CHAT ERROR:", str(e))
            raise 
            
            
            import json
            import re
            
            # Robust JSON extraction
            cleaned = response.text.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()

            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                pkg = json.loads(json_match.group(0))
                return {
                    "decisions": pkg.get("decisions", []),
                    "advice": pkg.get("advice", "Strategy formulation complete.")
                }
            
            try:
                pkg = json.loads(cleaned)
                return {
                    "decisions": pkg.get("decisions", []),
                    "advice": pkg.get("advice", "Strategy formulation complete.")
                }
            except:
                return {"decisions": [], "advice": "Core strategic directives finalized. Posture optimized for current market signals."}
        except Exception as e:
            logger.error(f"Failed to generate decision package: {e}")
            return {"decisions": [], "advice": "Strategic reasoning paused due to system signal."}
    async def generate_visualization_config(self, metrics: Dict, categories: Dict) -> Dict:
        """
        Asks Gemini to decide on the best visualization for the given data.
        Returns a dict: {"type": str, "title": str, "data": List[Dict], "description": str}
        """
        prompt = f"""
        You are a Data Visualization Expert. Given these business metrics and category performance, 
        select the single most impactful visualization to show a business owner.
        
        METRICS: {metrics}
        CATEGORIES: {categories}
        
        CHART TYPES AVAILABLE: "bar", "line", "area", "pie"
        
        TASK:
        1. Choose the best chart type.
        2. Provide a descriptive title.
        3. Format the data precisely for Recharts (array of objects with 'name' and 'value' keys).
        4. Provide a 1-sentence description of what this chart reveals.
        
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
            self._ensure_init()
            model_name = settings.GEMINI_MODELS.get("flash", "gemini-2.5-flash")
            
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=model_name,
                contents=prompt,
                config=gen_types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=VisualizationConfig
                )
            )
            
            if response and response.parsed:
                return response.parsed.model_dump()
            
            # If parsing failed but response text exists, try manual parse as backup
            if response and response.text:
                logger.warning(f"Structured parse failed, attempting manual parse of: {response.text[:100]}...")
                import json
                import re
                cleaned = response.text.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                    
            return self._fallback_visualization(categories)
        except Exception as e:
            logger.error(f"Failed to generate visualization config: {e}", exc_info=True)
            return self._fallback_visualization(categories)

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
