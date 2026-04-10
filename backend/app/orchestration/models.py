from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    STRICT = "STRICT"
    RESILIENT = "RESILIENT"


class PipelineStatus(str, Enum):
    """Lifecycle states for a pipeline execution."""
    PENDING = "PENDING"      # created but not yet started
    RUNNING = "RUNNING"      # currently executing
    COMPLETED = "COMPLETED"  # all steps finished successfully
    FAILED = "FAILED"        # execution raised an unrecoverable error


class PipelineState(BaseModel):
    # ── Identity ──────────────────────────────────────────────────────────────
    session_id: str

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    status: PipelineStatus = PipelineStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # ── Stage outputs ─────────────────────────────────────────────────────────
    raw_data: Optional[Any] = None
    features: Optional[Any] = None
    insights: Optional[Any] = None
    predictions: Optional[Any] = None
    decisions: Optional[Any] = None
    simulation: Optional[Any] = None

    # ── Arbitrary metadata (error info, mode, versions, …) ───────────────────
    metadata: dict = Field(default_factory=dict)

    # ── Computed helpers ──────────────────────────────────────────────────────
    @property
    def duration_seconds(self) -> Optional[float]:
        """Wall-clock execution time, or None if the pipeline is still running."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    model_config = {"arbitrary_types_allowed": True}
