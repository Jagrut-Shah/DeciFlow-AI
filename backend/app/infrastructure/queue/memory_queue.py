import asyncio
import logging
import time
from app.domain.interfaces.queue import ITaskQueue, ITaskRegistry
from app.domain.models.queue import TaskMessage

logger = logging.getLogger(__name__)

class MemoryQueue(ITaskQueue):
    def __init__(self, registry: ITaskRegistry, max_size: int = 1000):
        self._queue = asyncio.Queue(maxsize=max_size)
        self._registry = registry
        self._running = False
        self._workers = []

    async def enqueue(self, task: TaskMessage) -> None:
        try:
            await self._queue.put(task)
            logger.info(f"Task '{task.task_id}' ({task.task_name}) enqueued successfully.")
        except asyncio.QueueFull:
            logger.error(f"Queue is full. Task '{task.task_id}' rejected.")
            raise RuntimeError("Queue backpressure limit reached.")

    def get_metrics(self) -> dict:
        """Returns the current size of the queue and the number of active workers."""
        return {
            "size": self._queue.qsize(),
            "workers": len(self._workers)
        }

    async def _process_task(self, task: TaskMessage) -> None:
        handler = self._registry.get_handler(task.task_name)
        if not handler:
            logger.error(f"No handler registered for task '{task.task_name}'. Dead-lettering task '{task.task_id}'.")
            return
            
        try:
            from app.core.config import settings
            start_time = time.time()
            logger.info(f"[{task.trace_id}] Executing task '{task.task_id}' ({task.task_name}) - attempt {task.retries + 1}")
            
            # Use wait_for to enforce a timeout on the task execution
            await asyncio.wait_for(handler.handle(task), timeout=settings.TASK_TIMEOUT)
            
            elapsed = time.time() - start_time
            logger.info(f"[{task.trace_id}] Task '{task.task_id}' COMPLETED successfully in {elapsed:.4f}s.")
        except asyncio.TimeoutError:
             logger.error(f"[{task.trace_id}] Task '{task.task_id}' TIMED OUT after {settings.TASK_TIMEOUT}s")
             raise  # Re-raise to trigger the retry logic below
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[{task.trace_id}] Task '{task.task_id}' FAILED after {elapsed:.4f}s: {str(e)}")
            
            if task.retries < task.max_retries:
                task.retries += 1
                backoff_time = 2 ** task.retries
                logger.warning(f"[{task.trace_id}] Retrying task '{task.task_id}' in {backoff_time}s (Attempt {task.retries}/{task.max_retries})")
                
                # Re-enqueue in background to not block consumer
                asyncio.create_task(self._delay_requeue(task, backoff_time))
            else:
                logger.critical(f"[{task.trace_id}] Task '{task.task_id}' exceeded max retries. DEAD-LETTERING. Final error: {str(e)}")

    async def _delay_requeue(self, task: TaskMessage, delay: int):
        await asyncio.sleep(delay)
        await self.enqueue(task)

    async def start_consuming(self, concurrency: int = 5) -> None:
        self._running = True
        logger.info(f"Starting {concurrency} queue workers...")
        
        for i in range(concurrency):
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)

    async def _worker_loop(self, worker_id: int):
        logger.info(f"Worker {worker_id} started.")
        while self._running or not self._queue.empty():
            try:
                # Use timeout to allow checking self._running gracefully
                task: TaskMessage = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._process_task(task)
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} encountered critical error: {str(e)}")
        
        logger.info(f"Worker {worker_id} stopped.")

    async def stop_consuming(self) -> None:
        logger.info("Initiating graceful shutdown of MemoryQueue...")
        self._running = False
        
        # Wait for queue to drain if tasks exist
        if not self._queue.empty():
            logger.info("Draining remaining tasks...")
            await self._queue.join()
            
        # Cancel any hanging workers
        for worker in self._workers:
            if not worker.done():
                worker.cancel()
                
        # Wait for tasks to confirm cancellation
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            
        logger.info("MemoryQueue shut down successfully.")
