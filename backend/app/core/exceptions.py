"""
Global Exception Handlers
--------------------------
CustomException   — handled structured error, returns typed JSON.
generic_exception — catches any unhandled Exception, logs full traceback
                     internally with trace_id, but returns a safe 500
                     response that does NOT leak stack traces to the client.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from app.schemas.response import error_response
from app.observability.tracing import get_trace_id

logger = logging.getLogger(__name__)


class CustomException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "BAD_REQUEST",
        meta: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.meta = meta or {}
        super().__init__(self.message)


async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    """
    Returns a standardized JSON error for known CustomExceptions.
    """
    trace_id = get_trace_id()

    logger.warning(
        f"CustomException [{exc.error_code}]: {exc.message}",
        extra={"trace_id": trace_id, "path": request.url.path, "status_code": exc.status_code},
    )

    # Note: the trace_id is automatically attached by error_response helper
    response = error_response(
        message=exc.message, 
        data={"error_code": exc.error_code, "meta": exc.meta}
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all for any unhandled Exception.
    """
    from app.observability.metrics import metrics
    metrics.increment("requests_errors_total")
    metrics.increment("unhandled_exceptions_total")

    trace_id = get_trace_id()

    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}",
        exc_info=exc,
        extra={
            "trace_id": trace_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
    )

    response = error_response(
        message="An unexpected internal error occurred. Our team has been notified."
    )
    return JSONResponse(status_code=500, content=response.model_dump())
