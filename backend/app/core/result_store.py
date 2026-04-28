import asyncio
import logging
import time
import json
import os
from typing import Optional, Dict, Tuple

from app.orchestration.models import PipelineState
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResultStore:
    """
    Lightweight in-memory store for completed pipeline results,
    persisted to a local JSON file to survive server reloads.
    """

    _store: Dict[str, Tuple[PipelineState, float]] = {}
    _lock = asyncio.Lock()
    _disk_lock = asyncio.Lock()
    _last_eviction = time.time()

    def __init__(self, db_path: str = "data/db.json") -> None:
        self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Load only if the shared store is empty
        if not ResultStore._store:
            self._load_from_disk()

    def _load_from_disk(self):
        if not os.path.exists(self.db_path):
            return
        try:
            with open(self.db_path, "r") as f:
                data = json.load(f)
                for session_id, record in data.items():
                    try:
                        state = PipelineState.model_validate(record["state"])
                        self._store[session_id] = (state, record["timestamp"])
                    except Exception as rec_err:
                        logger.warning(f"ResultStore: skipping corrupt record {session_id}: {rec_err}")
            logger.info(f"ResultStore: loaded {len(self._store)} records from disk.")
        except Exception as e:
            logger.error(f"ResultStore: failed to load from disk: {e}")

    def _save_to_disk(self):
        try:
            data = {
                session_id: {
                    # Keep raw_data for frontend rendering; exclude heavy internal features
                    "state": state.model_dump(mode="json"),
                    "timestamp": ts
                }
                for session_id, (state, ts) in self._store.items()
            }
            with open(self.db_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"ResultStore: failed to save to disk: {e}")

    async def save_result(self, session_id: str, state: PipelineState) -> None:
        """Persist a completed PipelineState under session_id."""
        async with self._lock:
            # Periodically prune old results during save (amortized cleanup)
            if time.time() - self._last_eviction > 300: # Every 5 mins
                self._evict_expired()
                
            self._store[session_id] = (state, time.time())
            
            # Create a snapshot for disk persistence to release the lock immediately
            # We only persist a subset to keep the DB file manageable
            snapshot = {
                sid: {
                    "state": s.model_dump(mode="json"),
                    "timestamp": t
                }
                for sid, (s, t) in self._store.items()
            }
        
        # Disk I/O happens OUTSIDE the memory lock, but INSIDE a dedicated disk lock
        # to ensure snapshots are written sequentially and never out of order.
        try:
            async with self._disk_lock:
                await asyncio.to_thread(self._save_snapshot_to_disk, snapshot)
        except Exception as e:
            logger.error(f"ResultStore: non-blocking save failed: {e}")
            
        logger.info(
            "ResultStore: result saved to memory and queued for disk",
            extra={"session_id": session_id, "total_stored": len(self._store)},
        )

    def _save_snapshot_to_disk(self, snapshot: dict):
        """Internal helper to write a pre-captured snapshot to disk."""
        try:
            with open(self.db_path, "w") as f:
                json.dump(snapshot, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"ResultStore: failed to write snapshot to disk: {e}")

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

    async def get_latest_result(self) -> Optional[PipelineState]:
        """Retrieve the most recently saved PipelineState."""
        async with self._lock:
            if not self._store:
                return None
            # Find the entry with the highest timestamp
            latest_session_id = max(self._store.keys(), key=lambda k: self._store[k][1])
            return self._store[latest_session_id][0]

    async def get_result(self, session_id: str) -> Optional[PipelineState]:
        """
        Retrieve a stored PipelineState by session_id.
        No lock needed for simple dictionary read in Python (thread-safe for GIL),
        and it's okay if we get a slightly stale result vs. blocking the whole API.
        """
        entry = self._store.get(session_id)
        if entry:
            return entry[0]
        
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
