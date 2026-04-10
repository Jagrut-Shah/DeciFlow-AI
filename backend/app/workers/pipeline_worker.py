import logging
from typing import Dict, Any
from app.domain.interfaces.queue import ITaskHandler
from app.orchestration.engine import WorkflowEngine
from app.orchestration.models import ExecutionMode
from app.domain.models.queue import TaskMessage

logger = logging.getLogger(__name__)

class PipelineWorker(ITaskHandler):
    """
    STRICT RULE: No business logic! Delegation only.
    Responsible for retrieving WorkflowEngine and executing it.
    """
    def __init__(self, engine: WorkflowEngine):
        self._engine = engine

    async def handle(self, task: TaskMessage) -> None:
        from app.observability.tracing import start_trace, end_trace

        session_id = task.payload.get("session_id")
        data_payload = task.payload.get("payload", {})
        trace_id = task.trace_id

        # Restore trace context for this worker thread/async task
        start_trace(trace_id)

        try:
            logger.info(
                "PipelineWorker received task",
                extra={
                    "session_id": session_id,
                    "payload_keys": list(data_payload.keys()),
                    "payload_is_empty": len(data_payload) == 0,
                    "trace_id": trace_id,
                }
            )

            # Execute the pipeline — business logic is strictly inside the engine
            await self._engine.execute_pipeline(
                session_id=session_id,
                payload=data_payload,
                mode=ExecutionMode.RESILIENT,
            )

            logger.info(
                "PipelineWorker: session completed successfully",
                extra={"session_id": session_id, "trace_id": trace_id},
            )
        finally:
            end_trace()

