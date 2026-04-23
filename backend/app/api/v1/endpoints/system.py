from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.dependencies import get_task_queue
from app.infrastructure.queue.memory_queue import MemoryQueue
from app.schemas.response import APIResponse, success_response

router = APIRouter()

@router.get("/status", response_model=APIResponse)
async def get_system_status(
    queue: MemoryQueue = Depends(get_task_queue),
):
    """
    Returns the current operational status of the system, including
    queue depth, active worker count, and total system uptime.
    """
    # We import get_uptime_string here to avoid circular dependencies if main.py 
    # ever starts importing from endpoints.
    from app.main import get_uptime_string
    
    queue_metrics = queue.get_metrics()
    
    status_data = {
        "status": "healthy",
        "queue_size": queue_metrics["size"],
        "active_workers": queue_metrics["workers"],
        "uptime": get_uptime_string(),
        "version": "v1"
    }
    
    return success_response(
        data=status_data,
        message="System status retrieved successfully."
    )
