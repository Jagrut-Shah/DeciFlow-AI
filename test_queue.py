import sys
import os
import asyncio
import logging

sys.path.append(os.path.abspath(r"c:\Users\HP\Downloads\DeciFlow AI\backend"))

from app.domain.models.queue import TaskMessage
from app.infrastructure.queue.memory_queue import MemoryQueue
from app.infrastructure.queue.registry import TaskRegistry
from app.domain.interfaces.queue import ITaskHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DummyFailingWorker(ITaskHandler):
    def __init__(self):
        self.attempts = 0

    async def handle(self, payload: dict) -> None:
        self.attempts += 1
        if self.attempts < 3:
            logger.warning(f"Dummy worker failing intentionally on attempt {self.attempts}...")
            raise RuntimeError("Temporary simulated failure")
        logger.info(f"Dummy worker succeeding on attempt {self.attempts}!")

async def main():
    print("--- Booting Autonomous Queue Engine Test ---")
    
    registry = TaskRegistry()
    queue = MemoryQueue(registry=registry)
    
    # Register our dummy worker
    registry.register("test_flaky_task", DummyFailingWorker())
    
    # Start consumer loop
    await queue.start_consuming(concurrency=1)
    
    # Dispatch a task
    task = TaskMessage(
        task_id="JOB_TEST_84",
        task_name="test_flaky_task",
        payload={"data": 42},
        trace_id="TRACE_999",
        max_retries=3
    )
    
    await queue.enqueue(task)
    
    # Wait some time to let exponential backoff & retries happen
    print("[Waiting 10 seconds for backoffs to complete...]")
    await asyncio.sleep(10)
    
    # Shutdown queue gracefully
    await queue.stop_consuming()
    
    print("--- Test Completed ---")

if __name__ == "__main__":
    asyncio.run(main())
