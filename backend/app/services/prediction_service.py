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

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        metrics.increment("pipeline_predictions_total")

        # --- Fallback: empty or fallback insights ---
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

        logger.info(f"PredictionService: score={prediction_score}, confidence={insight_confidence}, anomaly={anomaly}.")

        return {
            "prediction_score": prediction_score,
            "confidence": insight_confidence,
            "probabilities": {"positive": positive_prob, "negative": negative_prob},
            "_fallback": False,
        }
