"""
InsightService — Pipeline Step 3
----------------------------------
Derives structured insights from extracted features.
CONTRACT:
  Input : features from FeatureService
  Output: {
      "insights_summary": str,         # human-readable summary
      "top_signal": str,               # most significant feature key
      "confidence": float,             # 0.0–1.0 derived from feature richness
      "anomaly_detected": bool,
      "context": str,                  # passed through for DecisionEngine
      "metrics_snapshot": Dict,        # numeric features passed through
      "_fallback": bool
  }
"""

import logging
from typing import Any, Dict
from app.domain.interfaces.insight_service import IInsightService
from app.observability.metrics import metrics

logger = logging.getLogger(__name__)


class InsightService(IInsightService):

    def generate_insights(self, features: Dict[str, Any]) -> Dict[str, Any]:
        metrics.increment("pipeline_insights_total")

        numeric = features.get("numeric", {}) if features else {}
        feature_count = features.get("feature_count", 0) if features else 0

        # --- Fallback: empty features ---
        if not features or features.get("_fallback") or feature_count == 0:
            logger.warning("InsightService: no features available. Returning insufficient_data insight.")
            return {
                "insights_summary": "insufficient_data",
                "top_signal": "none",
                "confidence": 0.0,
                "anomaly_detected": False,
                "context": "no_context",
                "metrics_snapshot": {},
                "_fallback": True,
            }

        # Derive confidence from feature richness (more features → more confident)
        confidence = min(1.0, feature_count / 10.0)

        # Identify top signal: numeric feature with highest absolute value
        top_signal = "none"
        if numeric:
            top_signal = max(numeric, key=lambda k: abs(numeric[k]))

        # Simple anomaly heuristic: any numeric value > 1000 or < -100
        anomaly = any(abs(v) > 1000 or v < -100 for v in numeric.values())

        summary = (
            f"Analyzed {feature_count} features. "
            f"Top signal: '{top_signal}'. "
            f"Confidence: {confidence:.0%}. "
            f"{'⚠ Anomaly detected.' if anomaly else 'No anomalies detected.'}"
        )

        logger.info(f"InsightService: {summary}")

        return {
            "insights_summary": summary,
            "top_signal": top_signal,
            "confidence": confidence,
            "anomaly_detected": anomaly,
            "context": summary,
            "metrics_snapshot": numeric,
            "_fallback": False,
        }
