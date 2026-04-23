"""
DecisionService — Orchestrates DecisionIntelligenceEngine
-----------------------------------------------------------
This is the bridge between the pipeline's InsightService/PredictionService
output and the DecisionIntelligenceEngine's internal pipeline
(generate → constrain → score → rank → explain).

CONTRACT:
  Input : context dict from WorkflowEngine (containing pipeline results):
    {
        "session_id": str,
        "insights": {               # from InsightService
            "context": str,
            "confidence": float,
            "metrics_snapshot": dict,
            ...
        },
        "predictions": {            # from PredictionService
            "prediction_score": float,
            "confidence": float,
            "probabilities": dict,
            ...
        },
    }

  Output:
    {
        "action": str,              # e.g. "REDUCE_PRICE"
        "score": float,
        "impact": float,
        "confidence": float,
        "feasibility": float,
        "explanation": str,
        "_fallback": bool
    }
"""

import logging
import uuid
from typing import Any, Dict

from app.domain.interfaces.decision_service import IDecisionService
from app.decision_engine.engine import DecisionIntelligenceEngine
from app.decision_engine.models import InsightInput, PredictionInput
from app.observability.metrics import metrics

logger = logging.getLogger(__name__)


class DecisionService(IDecisionService):

    def __init__(self, engine: DecisionIntelligenceEngine):
        self._engine = engine

    def orchestrate_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        metrics.increment("pipeline_decisions_total")

        insights_data = context.get("insights") or {}
        predictions_data = context.get("predictions") or {}

        # --- Fallback: missing both critical inputs ---
        if not insights_data and not predictions_data:
            logger.warning("DecisionService: no insights or predictions in context. Triggering fallback.")
            return self._fallback("No insights or predictions available.")

        # Build typed inputs for the DecisionIntelligenceEngine
        insight_input = InsightInput(
            insight_id=context.get("session_id") or str(uuid.uuid4()),
            context=insights_data.get("context") or insights_data.get("insights_summary") or "no_context",
            metrics=insights_data.get("metrics_snapshot") or {},
        )

        prediction_input = PredictionInput(
            prediction_id=str(uuid.uuid4()),
            probabilities=predictions_data.get("probabilities") or {"positive": 0.5, "negative": 0.5},
            confidence=float(predictions_data.get("confidence") or insights_data.get("confidence") or 0.5),
        )

        try:
            from app.observability.tracing import get_trace_id as _get_trace_id
            engine_trace_id = _get_trace_id() or context.get("session_id")
            decision_output = self._engine.execute_pipeline(
                insight_input, prediction_input, trace_id=engine_trace_id
            )
        except Exception as e:
            logger.error(f"DecisionService: engine failure: {e}", exc_info=True)
            return self._fallback(f"Engine exception: {e}")

        logger.info(f"DecisionService: decision='{decision_output.action}', score={decision_output.score:.3f}.")

        return {
            "action": decision_output.action,
            "score": decision_output.score,
            "impact": decision_output.impact,
            "confidence": decision_output.confidence,
            "feasibility": decision_output.feasibility,
            "explanation": decision_output.explanation,
            "_fallback": False,
        }

    @staticmethod
    def _fallback(reason: str) -> Dict[str, Any]:
        return {
            "action": "NO_ACTION",
            "score": 0.0,
            "impact": 0.0,
            "confidence": 0.0,
            "feasibility": 0.0,
            "explanation": f"Fallback triggered: {reason}",
            "_fallback": True,
        }
