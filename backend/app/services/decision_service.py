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

    async def orchestrate_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        metrics.increment("pipeline_decisions_total")

        # BRIDGE: Route to DecisionAgent for hybrid (rules + CSO advisory) logic
        from app.agents.decision_agent import DecisionAgent
        agent = DecisionAgent()

        # Format input for agent (DecisionAgent expects lists of insights and predictions)
        insights_data = context.get("insights", {})
        predictions_data = context.get("predictions", {})
        
        # Combine predictions list with high-level score
        all_predictions = predictions_data.get("predictions", [])
        if not all_predictions:
            all_predictions = [
                {
                    "text": f"Performance score is {predictions_data.get('prediction_score', 0.5):.2f}",
                    "confidence": predictions_data.get("confidence", 0.5)
                }
            ]
        
        agent_input = {
            "insights": insights_data.get("all_insights", []),
            "main_insight": {"text": insights_data.get("insights_summary")},
            "predictions": all_predictions,
            "mode": context.get("mode")
        }

        agent_result = await agent.execute(agent_input)

        if agent_result.get("status") != "ok":
            logger.warning(f"DecisionService: Agent failed ({agent_result.get('error')}). Using engine fallback.")
            return self._engine_fallback(context)

        # Map agent output back to service contract
        decisions = agent_result.get("decisions", [])
        top_decision = decisions[0] if decisions else self._fallback("No decisions generated")
        
        # If fallback was returned from _fallback, it will have 'action'
        if isinstance(top_decision, str): # Should not happen with current logic
             return self._fallback("Decision error")

        return {
            "action": top_decision.get("action", "NO_ACTION"),
            "strategy": top_decision.get("strategy", top_decision.get("action", "NO_ACTION")),
            "score": 0.8, # Base score from agent hierarchy
            "impact": 0.9 if top_decision.get("priority") == "high" else (0.6 if top_decision.get("priority") == "medium" else 0.3),
            "confidence": top_decision.get("confidence", 0.85),
            "feasibility": 0.8,
            "explanation": top_decision.get("reason", "No reason provided."),
            "ai_strategic_advice": agent_result.get("ai_strategic_advice"),
            "all_decisions": decisions,
            "_fallback": False,
        }

    def _engine_fallback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Original engine-based logic as a reliable fallback."""
        insights_data = context.get("insights") or {}
        predictions_data = context.get("predictions") or {}
        
        if not insights_data and not predictions_data:
            return self._fallback("No insights or predictions available.")

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
            decision_output = self._engine.execute_pipeline(insight_input, prediction_input)
            return {
                "action": decision_output.action,
                "score": decision_output.score,
                "impact": decision_output.impact,
                "confidence": decision_output.confidence,
                "feasibility": decision_output.feasibility,
                "explanation": decision_output.explanation,
                "_fallback": True,
            }
        except Exception as e:
            return self._fallback(str(e))

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
