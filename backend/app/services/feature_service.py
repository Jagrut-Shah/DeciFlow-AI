"""
FeatureService — Pipeline Step 2
----------------------------------
Extracts typed features from processed data output.
CONTRACT:
  Input : processed_data from DataService (contains "raw" and "fields")
  Output: {
      "numeric":   Dict[str, float],   # numeric features
      "boolean":   Dict[str, bool],    # boolean features
      "text":      Dict[str, str],     # text features
      "feature_count": int,
      "_fallback": bool
  }
"""

import logging
from typing import Any, Dict
from app.domain.interfaces.feature_service import IFeatureService
from app.observability.metrics import metrics

logger = logging.getLogger(__name__)


class FeatureService(IFeatureService):

    def extract_features(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        metrics.increment("pipeline_features_total")

        raw = processed_data.get("raw", {}) if processed_data else {}

        # --- Fallback: no usable data ---
        if not raw or processed_data.get("_fallback"):
            logger.warning("FeatureService: empty or fallback data received. Returning fallback features.")
            return {"numeric": {}, "boolean": {}, "text": {}, "feature_count": 0, "_fallback": True}

        numeric: Dict[str, float] = {}
        boolean: Dict[str, bool] = {}
        text: Dict[str, str] = {}

        for key, value in raw.items():
            if isinstance(value, bool):
                boolean[key] = value
            elif isinstance(value, (int, float)):
                numeric[key] = float(value)
            elif isinstance(value, str):
                text[key] = value

        feature_count = len(numeric) + len(boolean) + len(text)
        logger.info(f"FeatureService: extracted {feature_count} features ({len(numeric)} numeric, {len(boolean)} bool, {len(text)} text).")

        return {
            "numeric": numeric,
            "boolean": boolean,
            "text": text,
            "feature_count": feature_count,
            "_fallback": False,
        }
