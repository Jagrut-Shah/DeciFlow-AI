"""
PredictionService — Pipeline Step 4
--------------------------------------
Derives prediction probabilities from insights.
CONTRACT:
  Input : insights from InsightService
  Output: {
      "prediction_score": float,       # 0.0–1.0
      "confidence": float,             # mirrors insight confidence
      "probabilities": {               # class probabilities
          "positive": float,
          "negative": float
      },
      "_fallback": bool
  }
"""

import logging
from typing import Any, Dict
from app.domain.interfaces.prediction_service import IPredictionService
from app.observability.metrics import metrics

logger = logging.getLogger(__name__)


class PredictionService(IPredictionService):

    async def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        metrics.increment("pipeline_predictions_total")

        # NEW: Handle combined input from WorkflowEngine
        features = input_data.get("features", input_data)
        raw_data = input_data.get("raw_data", {})

        # BRIDGE: Route to PredictionAgent for hybrid (heuristic + Vertex AI) logic
        from app.agents.prediction_agent import PredictionAgent
        agent = PredictionAgent()
        
        # Format input for agent (prioritise rich metrics from DataAgent)
        agent_input = {
            "metrics": raw_data.get("metrics", features.get("numeric", {})),
            "category_performance": raw_data.get("category_performance", features.get("categories", {})),
            "data_quality": raw_data.get("data_quality", features.get("data_quality", 100)),
            "mode": input_data.get("mode")
        }
        
        agent_result = await agent.execute(agent_input)

        if agent_result.get("status") != "ok":
            logger.error(f"PredictionService: agent execution failed. {agent_result.get('error')}")
            # Fallback to simple logic if agent fails
            return self._fallback_logic(features)

        # Map agent output back to service contract
        predictions = agent_result.get("predictions", [])
        
        # Calculate an aggregate score/confidence for the service contract
        avg_confidence = sum(p.get("confidence", 0.5) for p in predictions) / len(predictions) if predictions else 0.5
        
        return {
            "prediction_score": avg_confidence, # Use confidence as a proxy for score in the legacy contract
            "confidence": avg_confidence,
            "probabilities": {"positive": avg_confidence, "negative": round(1.0 - avg_confidence, 4)},
            "predictions": predictions,
            "_fallback": False,
        }

    def _fallback_logic(self, features: Dict[str, Any]) -> Dict[str, Any]:
        # --- Fallback: empty or fallback input ---
        if not features or features.get("_fallback"):
            logger.warning("PredictionService: empty or fallback input. Returning neutral prediction.")
            return {
                "prediction_score": 0.5,
                "confidence": 0.0,
                "probabilities": {"positive": 0.5, "negative": 0.5},
                "_fallback": True,
            }

        # Use insight confidence as prediction base
        insight_confidence = features.get("confidence", 0.5)
        anomaly = features.get("anomaly_detected", False)

        # Anomaly reduces prediction score
        prediction_score = insight_confidence * (0.6 if anomaly else 1.0)
        prediction_score = round(max(0.0, min(1.0, prediction_score)), 4)

        positive_prob = prediction_score
        negative_prob = round(1.0 - positive_prob, 4)

        return {
            "prediction_score": prediction_score,
            "confidence": insight_confidence,
            "probabilities": {"positive": positive_prob, "negative": negative_prob},
            "_fallback": True,
        }
