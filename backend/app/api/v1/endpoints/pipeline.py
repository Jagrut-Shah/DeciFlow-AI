from fastapi import APIRouter, Depends, Query, BackgroundTasks, UploadFile, File, HTTPException
from typing import Optional
import uuid

from app.core.config import settings
from app.core.dependencies import get_workflow_engine, get_task_queue, get_result_store, get_data_service, get_trace_id
from app.domain.interfaces.data_service import IDataService
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

@router.post("/execute-from-file", response_model=APIResponse)
async def execute_from_file(
    request: Request,
    file: UploadFile = File(...),
    queue: MemoryQueue = Depends(get_task_queue),
    data_svc: IDataService = Depends(get_data_service)
):
    """
    Uploads a dataset and immediately runs the full AI pipeline (Data -> Feature -> Insight -> Prediction -> Decision -> Simulation).
    """
    session_id = str(uuid.uuid4())
    
    # 1. Read and Parse
    content = await file.read()
    filename_lower = file.filename.lower()
    
    if filename_lower.endswith(".csv"):
        parsed = data_svc.parse_csv_content(content)
    elif filename_lower.endswith(".json"):
        parsed = data_svc.parse_json_content(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .csv or .json")

    if isinstance(parsed, dict) and "error" in parsed:
        raise HTTPException(status_code=422, detail=f"Parsing error: {parsed['error']}")

    # 2. Extract and Normalize payload for the pipeline
    if isinstance(parsed, list):
        payload = {"data": parsed}
    elif isinstance(parsed, dict):
        if "data" in parsed and isinstance(parsed["data"], list):
            payload = parsed
        else:
            # If it's a single object, wrap it in a list
            payload = {"data": [parsed]}
    else:
        raise HTTPException(status_code=400, detail="Empty or invalid dataset provided.")

    if not payload["data"]:
        raise HTTPException(status_code=400, detail="Dataset contains no records.")

    # 3. Trigger Pipeline via MemoryQueue for better reliability/retries
    from app.infrastructure.queue.memory_queue import TaskMessage
    
    task = TaskMessage(
        task_id=session_id,
        task_name="workflow_pipeline",
        payload={
            "session_id": session_id,
            "payload": payload
        },
        max_retries=settings.MAX_RETRIES,
        trace_id=get_trace_id(request),
    )
    
    await queue.enqueue(task)

    logger.info(
        f"Pipeline triggered via queue: {session_id}",
        extra={"session_id": session_id, "record_count": count}
    )

    if isinstance(parsed, list):
        count = len(parsed)
    elif isinstance(parsed, dict):
        data = parsed.get("data")
        if isinstance(data, list):
            count = len(data)
        else:
            count = 1  # Single object record
    else:
        count = 1

    return success_response(
        data={
            "session_id": session_id,
            "status": "PENDING",
            "record_count": count
        },
        message=f"Pipeline triggered successfully. File: {file.filename}, Records: {count}. Tracking progress via session_id."
    )
