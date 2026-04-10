"""
AgentService — AI Agent Dispatcher
-------------------------------------
Routes agent execution requests to registered handlers.
CONTRACT (for Jeenal / AI Agents Team):

  Input to execute_agent(agent_name, context):
    agent_name: str    — one of "data_analyst", "insight_generator",
                         "decision_advisor", "risk_assessor"
    context: {
        "session_id": str,         # trace identifier
        "payload": Dict,           # raw input data for the agent
        "pipeline_stage": str,     # which stage is calling this agent
    }

  Output (always a dict, never raises):
    {
        "agent_name": str,
        "status": "success" | "unavailable" | "error",
        "result": Dict,            # agent-specific output (see below)
        "error": str | None
    }

  Agent-specific result schemas:
    "data_analyst"       → {"summary": str, "record_count": int, "quality_score": float}
    "insight_generator"  → {"key_insights": List[str], "confidence": float}
    "decision_advisor"   → {"recommendation": str, "risk": str}
    "risk_assessor"      → {"risk_level": str, "risk_score": float, "flags": List[str]}
"""

import logging
from typing import Any, Callable, Dict

from app.domain.interfaces.agent_service import IAgentService
from app.observability.metrics import metrics

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Stub handlers — Jeenal replaces these with real implementations     #
# ------------------------------------------------------------------ #

def _data_analyst_stub(context: Dict[str, Any]) -> Dict[str, Any]:
    payload = context.get("payload", {})
    return {
        "summary": f"Analyzed payload with {len(payload)} fields.",
        "record_count": len(payload),
        "quality_score": 0.85,
    }

def _insight_generator_stub(context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "key_insights": ["Trend is upward", "Anomaly in field 'revenue'"],
        "confidence": 0.78,
    }

def _decision_advisor_stub(context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "recommendation": "PROCEED",
        "risk": "medium",
    }

def _risk_assessor_stub(context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "risk_level": "medium",
        "risk_score": 0.45,
        "flags": [],
    }


# Registry maps agent_name → handler function
_AGENT_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "data_analyst":       _data_analyst_stub,
    "insight_generator":  _insight_generator_stub,
    "decision_advisor":   _decision_advisor_stub,
    "risk_assessor":      _risk_assessor_stub,
}


class AgentService(IAgentService):

    async def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        metrics.increment("agent_executions_total")

        handler = _AGENT_REGISTRY.get(agent_name)

        if handler is None:
            logger.warning(f"AgentService: unknown agent '{agent_name}'. Returning unavailable response.")
            metrics.increment("agent_unavailable_total")
            return {
                "agent_name": agent_name,
                "status": "unavailable",
                "result": {},
                "error": f"No handler registered for agent '{agent_name}'.",
            }

        try:
            result = handler(context)
            logger.info(f"AgentService: agent '{agent_name}' executed successfully.")
            return {
                "agent_name": agent_name,
                "status": "success",
                "result": result,
                "error": None,
            }
        except Exception as e:
            logger.error(f"AgentService: agent '{agent_name}' failed: {e}")
            metrics.increment("agent_errors_total")
            return {
                "agent_name": agent_name,
                "status": "error",
                "result": {},
                "error": str(e),
            }
