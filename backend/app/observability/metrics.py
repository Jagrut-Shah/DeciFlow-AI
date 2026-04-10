"""
MetricsCollector — In-memory metrics with Prometheus-compatible naming
-----------------------------------------------------------------------
Tracks counters and latency histograms for key application events.
Designed to be replaced by a real Prometheus client or Cloud Monitoring
exporter without changing call sites.

Pre-tracked metrics:
  requests_total          — all HTTP requests
  requests_errors_total   — HTTP 4xx/5xx responses
  pipeline_executions_total
  pipeline_failures_total
  queue_tasks_total
  queue_tasks_failed_total
"""

import threading
import time
from collections import defaultdict
from typing import Dict, List, Any


class MetricsCollector:
    """
    Thread-safe singleton metrics collector.

    Usage:
        metrics = MetricsCollector.instance()
        metrics.increment("requests_total")
        metrics.record_latency("pipeline_latency_ms", 142.5)
        snapshot = metrics.get_snapshot()
    """

    _instance: "MetricsCollector | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "MetricsCollector":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._counters: Dict[str, int] = defaultdict(int)
                    inst._latencies: Dict[str, List[float]] = defaultdict(list)
                    inst._counter_lock = threading.Lock()
                    inst._latency_lock = threading.Lock()
                    cls._instance = inst
        return cls._instance

    @classmethod
    def instance(cls) -> "MetricsCollector":
        return cls()

    # ------------------------------------------------------------------ #
    # Counters                                                             #
    # ------------------------------------------------------------------ #

    def increment(self, metric: str, by: int = 1) -> None:
        """Increment a named counter."""
        with self._counter_lock:
            self._counters[metric] += by

    def get_counter(self, metric: str) -> int:
        with self._counter_lock:
            return self._counters.get(metric, 0)

    # ------------------------------------------------------------------ #
    # Latency / Histograms                                                 #
    # ------------------------------------------------------------------ #

    def record_latency(self, metric: str, duration_ms: float) -> None:
        """Record a latency observation (milliseconds)."""
        with self._latency_lock:
            self._latencies[metric].append(duration_ms)
            # Keep a rolling window of 1000 observations per metric
            if len(self._latencies[metric]) > 1000:
                self._latencies[metric] = self._latencies[metric][-1000:]

    def get_latency_summary(self, metric: str) -> Dict[str, Any]:
        """Return p50/p95/p99/avg/max for a latency metric."""
        with self._latency_lock:
            data = sorted(self._latencies.get(metric, []))

        if not data:
            return {"count": 0, "avg_ms": 0, "p50_ms": 0, "p95_ms": 0, "p99_ms": 0, "max_ms": 0}

        n = len(data)
        return {
            "count": n,
            "avg_ms": round(sum(data) / n, 2),
            "p50_ms": round(data[int(n * 0.50)], 2),
            "p95_ms": round(data[int(n * 0.95)], 2),
            "p99_ms": round(data[int(n * 0.99)], 2),
            "max_ms": round(data[-1], 2),
        }

    # ------------------------------------------------------------------ #
    # Snapshot                                                             #
    # ------------------------------------------------------------------ #

    def get_snapshot(self) -> Dict[str, Any]:
        """Return a full metrics snapshot suitable for a /metrics endpoint."""
        with self._counter_lock:
            counters = dict(self._counters)
        with self._latency_lock:
            latency_keys = list(self._latencies.keys())

        latencies = {k: self.get_latency_summary(k) for k in latency_keys}

        return {
            "counters": counters,
            "latencies": latencies,
        }

    def reset(self) -> None:
        """Reset all metrics (useful in tests)."""
        with self._counter_lock:
            self._counters.clear()
        with self._latency_lock:
            self._latencies.clear()


# Module-level convenience alias
metrics = MetricsCollector.instance()
