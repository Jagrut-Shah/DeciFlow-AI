from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.domain.models.queue import TaskMessage

class ITaskHandler(ABC):
    @abstractmethod
    async def handle(self, task: TaskMessage) -> None:
        ...

class ITaskRegistry(ABC):
    @abstractmethod
    def register(self, task_name: str, handler: ITaskHandler) -> None:
        ...

    @abstractmethod
    def get_handler(self, task_name: str) -> Optional[ITaskHandler]:
        ...

class ITaskQueue(ABC):
    @abstractmethod
    async def enqueue(self, task: TaskMessage) -> None:
        ...

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Returns current queue depth and worker health snapshots."""
        ...
