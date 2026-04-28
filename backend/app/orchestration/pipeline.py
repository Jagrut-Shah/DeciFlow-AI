import time
import logging
import inspect
from typing import Callable, Any
from pydantic import BaseModel
from app.orchestration.models import PipelineState, ExecutionMode

logger = logging.getLogger(__name__)

class PipelineStep(BaseModel):
    name: str
    func: Callable[..., Any]
    input_key: str
    output_key: str

    model_config = {"arbitrary_types_allowed": True}


async def _execute_step(step: PipelineStep, state: PipelineState, mode: ExecutionMode) -> PipelineState:
    """
    Execute a single pipeline step with:
    - Monotonic timing (perf_counter)
    - Per-step metrics (counter + latency)
    - Trace ID in all log lines
    - Consistent fallback dict structure (_fallback=True) in RESILIENT mode
    """
    from app.observability.metrics import metrics
    from app.observability.tracing import get_trace_id

    trace_id = get_trace_id() or state.session_id
    start = time.perf_counter()
    input_data = getattr(state, step.input_key)

    logger.info(
        f"Pipeline step starting: {step.name}",
        extra={"trace_id": trace_id, "session_id": state.session_id, "step": step.name},
    )

    try:
        from app.core.config import settings
        import asyncio

        # Use settings.TASK_TIMEOUT as a safety net for all pipeline steps
        timeout = getattr(settings, "TASK_TIMEOUT", 30)

        if inspect.iscoroutinefunction(step.func):
            output = await asyncio.wait_for(step.func(input_data), timeout=timeout)
        else:
            # For sync functions, run in thread to avoid blocking loop
            output = await asyncio.wait_for(
                asyncio.to_thread(step.func, input_data), 
                timeout=timeout
            )

        setattr(state, step.output_key, output)

        elapsed_ms = (time.perf_counter() - start) * 1000
        metrics.increment(f"step_{step.name.lower()}_total")
        metrics.record_latency(f"step_{step.name.lower()}_ms", elapsed_ms)

        logger.info(
            f"Pipeline step succeeded: {step.name}",
            extra={"trace_id": trace_id, "session_id": state.session_id, "step": step.name, "elapsed_ms": round(elapsed_ms, 2)},
        )
        state.metadata[f"{step.name}_status"] = "SUCCESS"
        state.metadata[f"{step.name}_ms"] = round(elapsed_ms, 2)

    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        metrics.increment(f"step_{step.name.lower()}_failures_total")

        logger.error(
            f"Pipeline step failed: {step.name}",
            exc_info=True,
            extra={"trace_id": trace_id, "session_id": state.session_id, "step": step.name,
                   "elapsed_ms": round(elapsed_ms, 2), "error": str(e)},
        )
        state.metadata[f"{step.name}_status"] = "FAILED"
        state.metadata[f"{step.name}_ms"] = round(elapsed_ms, 2)

        if mode == ExecutionMode.STRICT:
            raise RuntimeError(f"Pipeline failed at step '{step.name}': {e}") from e
        else:
            # Use _fallback=True — all services check for this key and handle gracefully
            setattr(state, step.output_key, {"_fallback": True, "_error": str(e), "_step": step.name})

    return state
