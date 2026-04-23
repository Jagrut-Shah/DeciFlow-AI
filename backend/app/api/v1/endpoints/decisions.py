"""
Decisions Endpoint
-------------------
POST /decisions/decide — Runs decision orchestration directly.
"""

import logging
from fastapi import APIRouter, Depends, Request

from app.schemas.response import success_response, APIResponse
from app.schemas.v1.decisions import DecisionContext, DecisionResult
from app.core.dependencies import get_current_user, get_decision_service
from app.domain.interfaces.decision_service import IDecisionService
from app.observability.tracing import get_trace_id

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/decide",
    response_model=APIResponse,
    summary="Run decision orchestration",
    description=(
        "Accepts a context payload, runs through the DecisionIntelligenceEngine "
        "(generate → constrain → score → rank → explain), and returns the top recommended action."
    ),
)
async def get_decision(
    context: DecisionContext,
    current_user: dict = Depends(get_current_user),
    decision_service: IDecisionService = Depends(get_decision_service),
):
    trace_id = get_trace_id()
    
    decision_context = {
        "session_id": context.session_id,
        "insights": {
            "context": str(context.payload),
            "confidence": 0.7,
            "metrics_snapshot": {k: v for k, v in context.payload.items() if isinstance(v, (int, float))},
        },
        "predictions": {
            "prediction_score": 0.7,
            "confidence": 0.7,
            "probabilities": {"positive": 0.7, "negative": 0.3},
        },
    }

    result = decision_service.orchestrate_decision(context=decision_context)

    resp = DecisionResult(
        action=result.get("action", "NO_ACTION"),
        confidence_score=result.get("confidence", 0.0),
        score=result.get("score", 0.0),
        impact=result.get("impact", 0.0),
        feasibility=result.get("feasibility", 0.0),
        explanation=result.get("explanation", ""),
        alternatives=[],
        trace_id=trace_id,
        is_fallback=result.get("_fallback", False),
    )

    logger.info(
        f"Decision completed: action='{resp.action}', score={resp.score:.3f}",
        extra={"trace_id": trace_id, "session_id": context.session_id},
    )

    return success_response(data=resp)
