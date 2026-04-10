"""Pipeline request/response schemas."""

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class PipelineRunRequest(BaseModel):
    session_id: str = Field(..., description="Unique identifier for this pipeline run.")
    payload: Dict[str, Any] = Field(..., description="Raw input data for processing.")


class PipelineRunResponse(BaseModel):
    task_id: str = Field(..., description="Enqueued task ID (for async mode).")
    session_id: str
    status: str = Field(default="queued", description="'queued' | 'running' | 'completed'")
    trace_id: Optional[str] = None
    message: str = "Pipeline task enqueued successfully."
