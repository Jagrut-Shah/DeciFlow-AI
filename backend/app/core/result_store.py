import asyncio
import logging
import time
from typing import Optional, Dict, Tuple

from app.orchestration.models import PipelineState
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResultStore:
    """
    Lightweight in-memory store for completed pipeline results.
    Includes simple TTL-based eviction to prevent memory leaks.
    """

    def __init__(self) -> None:
        # Store is session_id -> (PipelineState, timestamp)
        self._store: Dict[str, Tuple[PipelineState, float]] = {}
        self._lock = asyncio.Lock()
        self._last_eviction = time.time()

    async def save_result(self, session_id: str, state: PipelineState) -> None:
        """Persist a completed PipelineState under session_id."""
        async with self._lock:
            # Periodically prune old results during save (amortized cleanup)
            if time.time() - self._last_eviction > 300: # Every 5 mins
                self._evict_expired()
                
            self._store[session_id] = (state, time.time())
            
        logger.info(
            "ResultStore: result saved",
            extra={"session_id": session_id, "total_stored": len(self._store)},
        )

    def _evict_expired(self) -> None:
        """Removes entries older than SETTINGS.RESULT_TTL. Must be called under lock."""
        now = time.time()
        expired_keys = [
            k for k, v in self._store.items() 
            if now - v[1] > settings.RESULT_TTL
        ]
        for k in expired_keys:
            del self._store[k]
        
        self._last_eviction = now
        if expired_keys:
            logger.info(f"ResultStore: evicted {len(expired_keys)} expired results")

    async def get_result(self, session_id: str) -> Optional[PipelineState]:
        """Retrieve a stored PipelineState by session_id."""
        async with self._lock:
            entry = self._store.get(session_id)
            if entry:
                # Update timestamp on read to keep 'hot' data? 
                # Decided: No, use absolute TTL from completion for deterministic memory management.
                return entry[0]
        
        logger.warning(
            "ResultStore: result not found",
            extra={"session_id": session_id},
        )
        return None

    async def delete_result(self, session_id: str) -> bool:
        """Remove a result manually."""
        async with self._lock:
            existed = self._store.pop(session_id, None) is not None
        if existed:
            logger.info("ResultStore: result deleted", extra={"session_id": session_id})
        return existed

    def size(self) -> int:
        return len(self._store)

    def clear(self) -> None:
        self._store.clear()
