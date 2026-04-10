"""
Middleware
----------
1. SecurityHeadersMiddleware   — injects production-grade HTTP security headers.
2. RequestLoggingMiddleware    — generates/propagates X-Trace-ID, logs structured
                                  request/response info, records metrics.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.observability.tracing import get_or_create_trace_id, end_trace
from app.observability.metrics import metrics

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects security-related HTTP response headers on every response.
    These are the minimal recommended headers for any production API.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        # Remove server fingerprinting header if present
        response.headers.pop("server", None)

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Per-request middleware that:
      - Generates or reuses an X-Trace-ID (UUID4).
      - Attaches trace_id to request.state for downstream access.
      - Propagates trace_id back in the response header.
      - Emits a structured JSON log entry per request.
      - Records request/error counters and latency via MetricsCollector.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # ---- Trace ID: reuse upstream header or generate fresh ----
        incoming_trace = request.headers.get("X-Trace-ID")
        trace_id = get_or_create_trace_id(incoming_trace)
        request.state.trace_id = trace_id

        start_time = time.perf_counter()
        metrics.increment("requests_total")

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        # ---- Propagate trace ID in response ----
        response.headers["X-Trace-ID"] = trace_id

        # ---- Metrics ----
        metrics.record_latency("request_latency_ms", duration_ms)
        if response.status_code >= 400:
            metrics.increment("requests_errors_total")

        # ---- Structured log ----
        logger.info(
            "request_completed",
            extra={
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

        end_trace()
        return response
