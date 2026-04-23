"""
DataService — Pipeline Step 1
------------------------------
Validates and normalizes inbound raw payload.
CONTRACT (for Aarwa / Data Team):
  Input : source: str, payload: Dict[str, Any]
  Output: {
      "source": str,
      "record_count": int,       # number of keys in payload
      "fields": List[str],       # top-level field names
      "raw": Dict[str, Any],     # sanitized original payload
      "_fallback": bool          # True if payload was empty/invalid
  }
"""

import logging
from typing import Any, Dict
from app.domain.interfaces.data_service import IDataService
from app.observability.metrics import metrics

logger = logging.getLogger(__name__)


class DataService(IDataService):

    def process_raw_data(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        metrics.increment("pipeline_data_total")

        # --- Fallback: empty or non-dict payload ---
        if not payload or not isinstance(payload, dict):
            logger.warning(f"DataService: empty or invalid payload from '{source}'. Returning fallback.")
            return {
                "source": source or "unknown",
                "record_count": 0,
                "fields": [],
                "raw": {},
                "_fallback": True,
            }

        # Sanitize string values (strip whitespace)
        sanitized: Dict[str, Any] = {}
        for k, v in payload.items():
            if isinstance(v, str):
                sanitized[k] = v.strip()
            elif isinstance(v, dict):
                sanitized[k] = {sk: sv.strip() if isinstance(sv, str) else sv for sk, sv in v.items()}
            else:
                sanitized[k] = v

        result = {
            "source": source,
            "record_count": len(sanitized),
            "fields": list(sanitized.keys()),
            "raw": sanitized,
            "_fallback": False,
        }

        logger.info(f"DataService: processed {result['record_count']} fields from '{source}'.")
        return result
