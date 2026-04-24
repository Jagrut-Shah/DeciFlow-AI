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

    async def generate_insights(self, features: Dict[str, Any]) -> Dict[str, Any]:
        metrics.increment("pipeline_insights_total")

        # BRIDGE: Route to InsightAgent for hybrid (heuristic + Vertex AI) logic
        from app.agents.insight_agent import InsightAgent
        agent = InsightAgent()
        
        # Format input for agent (numeric features are core)
        agent_input = {
            "metrics": features.get("numeric", {}),
            "category_performance": features.get("categories", {}),
            "data_quality": features.get("data_quality", 100)
        }
        
        agent_result = await agent.execute(agent_input)

        if agent_result.get("status") != "ok":
            logger.error(f"InsightService: agent execution failed. {agent_result.get('error')}")
            # Fallback to simple logic if agent fails
            return self._fallback_logic(features)

        # Map agent output back to service contract
        summary = agent_result.get("main_insight", {}).get("message", "Analysis complete.")
        
        return {
            "insights_summary": summary,
            "top_signal": agent_result.get("main_insight", {}).get("type", "none"),
            "confidence": 0.9 if agent_result.get("status") == "ok" else 0.5,
            "anomaly_detected": any(i.get("priority") == "high" for i in agent_result.get("insights", [])),
            "context": agent_result.get("ai_narrative", summary),
            "metrics_snapshot": features.get("numeric", {}),
            "all_insights": agent_result.get("insights", []),
            "_fallback": False,
        }

    def _fallback_logic(self, features: Dict[str, Any]) -> Dict[str, Any]:
        numeric = features.get("numeric", {}) if features else {}
        feature_count = features.get("feature_count", 0) if features else 0
        
        if not features or feature_count == 0:
            return {
                "insights_summary": "insufficient_data",
                "top_signal": "none",
                "confidence": 0.0,
                "anomaly_detected": False,
                "context": "no_context",
                "metrics_snapshot": {},
                "_fallback": True,
            }

        confidence = min(1.0, feature_count / 10.0)
        top_signal = max(numeric, key=lambda k: abs(numeric[k])) if numeric else "none"
        summary = f"Analyzed {feature_count} features. Top signal: '{top_signal}'."

        return {
            "insights_summary": summary,
            "top_signal": top_signal,
            "confidence": confidence,
            "anomaly_detected": False,
            "context": summary,
            "metrics_snapshot": numeric,
            "_fallback": True,
        }
