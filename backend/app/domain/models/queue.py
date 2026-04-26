from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TaskMessage(BaseModel):
    task_id: str
    task_name: str
    payload: Dict[str, Any]
    retries: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    trace_id: Optional[str] = None
