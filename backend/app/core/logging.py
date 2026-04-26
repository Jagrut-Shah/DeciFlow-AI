"""
Structured JSON Logging
-----------------------
Enriches every log record with: trace_id, environment, service_name,
and any extras passed via the `extra={}` kwarg on logger calls.

The trace_id is pulled from the active ContextVar set by tracing.py —
so any logger.info() call made inside a request automatically carries
the correct trace ID without needing to pass it around manually.
"""

import logging
import json
import sys
from datetime import datetime, timezone

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Outputs log records as single-line JSON objects with standard fields
    plus any extras passed via logger.info(..., extra={...}).
    """

    # Fields that logging.LogRecord always has — we don't want to double-emit them
    _INTERNAL_FIELDS = frozenset(
        LogRecord.__dict__.keys() if (LogRecord := logging.LogRecord) else []
    )

    def format(self, record: logging.LogRecord) -> str:
        # Pull trace_id from ContextVar (zero-friction automatic embedding)
        try:
            from app.observability.tracing import get_trace_id
            trace_id = get_trace_id()
        except Exception:
            trace_id = None

        log_entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level":     record.levelname,
            "logger":    record.name,
            "message":   record.getMessage(),
            "service":   settings.PROJECT_NAME,
            "env":       settings.ENVIRONMENT,
            "trace_id":  trace_id,
        }

        # Merge any `extra={...}` fields the caller provided,
        # skipping LogRecord internals to avoid noise
        _skip = {
            "args", "created", "exc_info", "exc_text", "filename", "funcName",
            "levelname", "levelno", "lineno", "message", "module", "msecs",
            "msg", "name", "pathname", "process", "processName", "relativeCreated",
            "stack_info", "taskName", "thread", "threadName",
        }
        for key, value in record.__dict__.items():
            if key not in _skip:
                log_entry[key] = value

        # Attach exception traceback if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


class TraceIDFilter(logging.Filter):
    """
    Enriches every LogRecord with a 'trace_id' attribute pulled from ContextVars.
    This ensures handlers/formatters see it even if not passed in extra={}.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            from app.observability.tracing import get_trace_id
            record.trace_id = get_trace_id()
        except Exception:
            record.trace_id = None
        return True


def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    root.setLevel(level)

    # Add the filter to the root logger so all records are enriched
    if not any(isinstance(f, TraceIDFilter) for f in root.filters):
        root.addFilter(TraceIDFilter())

    # Clear any pre-existing handlers (e.g. uvicorn default)
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)
