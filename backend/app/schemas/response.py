from typing import Any, Optional
from pydantic import BaseModel
from app.observability.tracing import get_trace_id

class APIResponse(BaseModel):
    """
    Standardized API Response Model.
    """
    status: str
    data: Optional[Any] = None
    message: str = ""
    trace_id: str

def success_response(data: Any, message: str = "") -> APIResponse:
    """
    Helper to create a standardized success response.
    Automatically fetches trace_id from the current context.
    """
    return APIResponse(
        status="success",
        data=data,
        message=message,
        trace_id=get_trace_id() or "unknown"
    )

def error_response(message: str, data: Any = None) -> APIResponse:
    """
    Helper to create a standardized error response.
    Automatically fetches trace_id from the current context.
    """
    return APIResponse(
        status="error",
        data=data,
        message=message,
        trace_id=get_trace_id() or "unknown"
    )
