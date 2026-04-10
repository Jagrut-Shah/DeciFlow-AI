import logging
from typing import Dict, Optional
from app.domain.interfaces.queue import ITaskRegistry, ITaskHandler

logger = logging.getLogger(__name__)

class TaskRegistry(ITaskRegistry):
    def __init__(self):
        self._handlers: Dict[str, ITaskHandler] = {}

    def register(self, task_name: str, handler: ITaskHandler) -> None:
        if task_name in self._handlers:
            logger.warning(f"Handler for task '{task_name}' is being overwritten.")
        self._handlers[task_name] = handler
        logger.info(f"Registered handler for task '{task_name}'.")

    def get_handler(self, task_name: str) -> Optional[ITaskHandler]:
        return self._handlers.get(task_name)
