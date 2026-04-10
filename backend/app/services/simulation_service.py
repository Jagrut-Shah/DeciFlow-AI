"""
SimulationService — Pipeline Step 6
--------------------------------------
Projects financial/operational outcomes from a decision output.
CONTRACT:
  Input : decision dict from DecisionService (contains score, confidence, action)
  Output: {
      "projected_roi": float,
      "risk_level": str,          # "low" | "medium" | "high"
      "recommendation": str,
      "decision_echo": dict,      # passthrough for auditability
      "_fallback": bool
  }
"""

import logging
from typing import Any, Dict
from app.domain.interfaces.simulation_service import ISimulationService
from app.observability.metrics import metrics

logger = logging.getLogger(__name__)


class SimulationService(ISimulationService):

    def simulate(self, decision: Any) -> Dict[str, Any]:
        metrics.increment("pipeline_simulations_total")

        # --- Fallback: None or non-dict decision ---
        if not decision or not isinstance(decision, dict):
            logger.warning("SimulationService: invalid decision input. Returning fallback simulation.")
            return {
                "projected_roi": 0.0,
                "risk_level": "unknown",
                "recommendation": "Insufficient decision data for simulation.",
                "decision_echo": {},
                "_fallback": True,
            }

        score = decision.get("score", 0.0) or 0.0
        confidence = decision.get("confidence", 0.0) or 0.0
        action = decision.get("action", "NO_ACTION")

        # ROI model: score * confidence scaled to a realistic multiplier (0.8–2.5x)
        projected_roi = round(0.8 + (score * confidence * 1.7), 4)
        projected_roi = max(0.0, min(5.0, projected_roi))  # cap at 5x

        # Risk level from confidence
        if confidence >= 0.8:
            risk = "low"
        elif confidence >= 0.5:
            risk = "medium"
        else:
            risk = "high"

        recommendation = (
            f"Execute '{action}' with {risk} risk profile. "
            f"Projected ROI: {projected_roi:.2f}x based on decision score {score:.3f}."
        )

        logger.info(f"SimulationService: ROI={projected_roi}, risk={risk}, action={action}.")

        return {
            "projected_roi": projected_roi,
            "risk_level": risk,
            "recommendation": recommendation,
            "decision_echo": decision,
            "_fallback": False,
        }
