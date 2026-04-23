from fastapi import APIRouter, Depends, Query, BackgroundTasks
from typing import Optional
import uuid

from app.core.config import settings
from app.core.dependencies import get_workflow_engine, get_task_queue, get_result_store
from app.core.exceptions import CustomException
from app.orchestration.engine import WorkflowEngine
from app.orchestration.models import ExecutionMode
from app.infrastructure.queue.memory_queue import MemoryQueue, TaskMessage
from app.core.result_store import ResultStore
from app.schemas.response import APIResponse, success_response

router = APIRouter()

@router.post("/run-sync", response_model=APIResponse)
async def run_pipeline_sync(
    payload: dict,
    mode: Optional[ExecutionMode] = Query(None, description="STRICT or RESILIENT execution"),
    engine: WorkflowEngine = Depends(get_workflow_engine),
):
    """
    Executes the AI pipeline synchronously.
    The response is returned only after all stages complete or one fails.
    """
    session_id = str(uuid.uuid4())
    try:
        # engine.execute_pipeline now uses settings.PIPELINE_MODE as its default_mode
        state = await engine.execute_pipeline(
            session_id=session_id,
            payload=payload,
            mode=mode,
        )
        return success_response(
            data=state.model_dump(),
            message="Pipeline completed successfully (Sync)"
        )
    except Exception as e:
        raise CustomException(
            message=f"Pipeline execution failed: {str(e)}",
            status_code=500,
            error_code="PIPELINE_ERROR"
        )


@router.post("/run", response_model=APIResponse)
async def run_pipeline_async(
    payload: dict,
    queue: MemoryQueue = Depends(get_task_queue),
):
    """
    Trigger the AI pipeline asynchronously.
    Returns a session_id immediately. Clients should poll /result/{session_id} for status.
    """
    session_id = str(uuid.uuid4())
    
    from app.observability.tracing import get_trace_id
    
    task = TaskMessage(
        task_id=session_id,
        task_name="workflow_pipeline",   # must match expected worker name in TaskRegistry
        payload={
            "session_id": session_id,
            "payload": payload
        },
        max_retries=settings.MAX_RETRIES,
        trace_id=get_trace_id(),
    )
    
    await queue.enqueue(task)
    
    return success_response(
        data={"session_id": session_id, "status": "PENDING"},
        message="Pipeline triggered successfully (Async)"
    )


@router.get("/{session_id}/result", response_model=APIResponse)
async def get_pipeline_result(
    session_id: str,
    store: Optional[ResultStore] = Depends(get_result_store),
):
    """
    Retrieve the current state/result of a pipeline execution by session_id.
    Returns 404 if the session_id is invalid or results have expired/been disabled.
    """
    if store is None:
        raise CustomException(
            message="Result storage is currently disabled in system settings.",
            status_code=400,
            error_code="STORAGE_DISABLED"
        )

    state = await store.get_result(session_id)
    if not state:
        raise CustomException(
            message=f"No results found for session_id: {session_id}",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    return success_response(
        data=state.model_dump(),
        message="Result retrieved successfully"
    )
