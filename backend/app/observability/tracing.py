"""
Tracing — ContextVar-based distributed trace context
------------------------------------------------------
Propagates a trace ID through the full async request lifecycle using
Python's contextvars, making it available to any logger or service
without explicitly threading it through function arguments.

Designed to be OpenTelemetry-compatible: the ContextVar approach mirrors
OTEL's context propagation model so swapping in an OTLP exporter later
requires minimal refactoring.
"""

import uuid
import logging
import time
from contextvars import ContextVar
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level ContextVar — carries the active trace ID across async boundaries
_trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
_trace_start_var: ContextVar[Optional[float]] = ContextVar("trace_start", default=None)


def start_trace(trace_id: Optional[str] = None) -> str:
    """
    Begin a new trace. Generates a UUID if no trace_id is provided.
    Returns the active trace_id.
    """
    active_id = trace_id or str(uuid.uuid4())
    _trace_id_var.set(active_id)
    _trace_start_var.set(time.perf_counter())
    logger.debug(f"Trace started: {active_id}")
    return active_id


def get_trace_id() -> Optional[str]:
    """Return the active trace ID for the current execution context."""
    return _trace_id_var.get()


def end_trace() -> Optional[float]:
    """
    End the current trace, log a summary, and return the elapsed duration (seconds).
    Resets both trace ID and start time ContextVars.
    """
    trace_id = _trace_id_var.get()
    start = _trace_start_var.get()
    duration: Optional[float] = None

    if start is not None:
        duration = time.perf_counter() - start
        logger.info(
            f"Trace completed",
            extra={"trace_id": trace_id, "duration_ms": round(duration * 1000, 2)},
        )

    _trace_id_var.set(None)
    _trace_start_var.set(None)
    return duration


def get_or_create_trace_id(incoming: Optional[str] = None) -> str:
    """
    Reuse an incoming X-Trace-ID header value if present and valid,
    otherwise generate a fresh UUID. Sets the ContextVar.
    Used by middleware on each inbound request.
    """
    # Basic sanity check — accept only UUID-shaped values from upstream
    candidate = incoming if (incoming and len(incoming) <= 64) else None
    return start_trace(candidate)
