"""
Result Store — in-memory pipeline result persistence.

Stores the final PipelineState keyed by session_id.
Thread-safe via asyncio.Lock for concurrent async access.
"""

import asyncio
import logging
from typing import Optional, Dict

from app.orchestration.models import PipelineState

logger = logging.getLogger(__name__)


class ResultStore:
    """
    Lightweight in-memory store for completed pipeline results.

    Design decisions:
    - asyncio.Lock: protects the dict from concurrent coroutine writes
      without blocking the event loop (unlike threading.Lock).
    - No TTL / eviction: results live for the process lifetime.
      Swap the dict for Redis/Firestore when persistence is needed.
    - Session IDs are caller-provided; no collision detection needed
      (the pipeline layer already generates unique UUIDs per run).
    """

    def __init__(self) -> None:
        self._store: Dict[str, PipelineState] = {}
        self._lock = asyncio.Lock()

    async def save_result(self, session_id: str, state: PipelineState) -> None:
        """Persist a completed PipelineState under session_id."""
        async with self._lock:
            self._store[session_id] = state
        logger.info(
            "ResultStore: result saved",
            extra={"session_id": session_id, "total_stored": len(self._store)},
        )

    async def get_result(self, session_id: str) -> Optional[PipelineState]:
        """
        Retrieve a stored PipelineState by session_id.
        Returns None if not found (caller decides how to handle 404).
        """
        async with self._lock:
            result = self._store.get(session_id)
        if result is None:
            logger.warning(
                "ResultStore: result not found",
                extra={"session_id": session_id},
            )
        return result

    async def delete_result(self, session_id: str) -> bool:
        """
        Remove a result by session_id. Returns True if it existed.
        Useful for cleanup after result retrieval in memory-sensitive scenarios.
        """
        async with self._lock:
            existed = self._store.pop(session_id, None) is not None
        if existed:
            logger.info(
                "ResultStore: result deleted",
                extra={"session_id": session_id},
            )
        return existed

    def size(self) -> int:
        """Return the number of stored results (non-blocking read for metrics)."""
        return len(self._store)

    def clear(self) -> None:
        """Synchronous clear — only for testing/teardown, not for concurrent use."""
        self._store.clear()
