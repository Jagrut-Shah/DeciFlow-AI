"""Decision-related API schemas."""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class DecisionContext(BaseModel):
    """Input schema for the /decide endpoint."""
    session_id: str = Field(..., description="Unique identifier for this decision request.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Raw context data for the decision.")
    mode: str = Field(default="standard", description="Processing mode: 'standard' | 'conservative'.")


class DecisionResult(BaseModel):
    """Output schema from the /decide endpoint."""
    action: str = Field(..., description="Recommended action name.")
    confidence_score: float = Field(..., description="Decision confidence (0.0–1.0).")
    score: float = Field(..., description="Composite decision score.")
    impact: float = Field(..., description="Projected impact (0.0–1.0).")
    feasibility: float = Field(..., description="Action feasibility (0.0–1.0).")
    explanation: str = Field(..., description="Human-readable explanation of the decision.")
    alternatives: List[str] = Field(default_factory=list)
    trace_id: Optional[str] = None
    is_fallback: bool = False
