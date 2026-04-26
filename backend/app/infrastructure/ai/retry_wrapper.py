import asyncio
import logging
import time
from typing import Callable, Coroutine, Any

logger = logging.getLogger(__name__)

async def with_retry(
    func: Callable[..., Coroutine[Any, Any, Any]],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    timeout: float = 30.0,
    **kwargs
) -> Any:
    for attempt in range(1, max_retries + 1):
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Attempt {attempt} timed out after {timeout}s.")
        except Exception as e:
            logger.warning(f"Attempt {attempt} failed: {str(e)}")
            
        if attempt == max_retries:
            logger.error(f"All {max_retries} attempts failed.")
            raise Exception("LLM interaction failed after max retries")
            
        delay = base_delay * (2 ** (attempt - 1))
        logger.info(f"Retrying in {delay}s...")
        await asyncio.sleep(delay)
