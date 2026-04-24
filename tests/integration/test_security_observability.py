"""
test_security_observability.py
-------------------------------
Integration tests for the Security + Observability layer.
Run with: python test_security_observability.py
(No pytest required — uses stdlib unittest)
"""

import sys
import os
import unittest
import time

# Point to backend so app.* imports resolve
sys.path.insert(0, os.path.abspath(r"c:\Users\HP\Downloads\DeciFlow AI\backend"))

# Override SECRET_KEY before settings loads to avoid validator crash in tests
os.environ["SECRET_KEY"] = "test-secret-key-safe-for-unit-tests-only-abc123"
os.environ["ENVIRONMENT"] = "development"


# ======================================================================= #
# Security — JWT                                                           #
# ======================================================================= #

class TestJWT(unittest.TestCase):

    def setUp(self):
        from app.core.security import create_access_token, create_refresh_token, verify_token
        self.create_access = create_access_token
        self.create_refresh = create_refresh_token
        self.verify = verify_token

    def test_create_and_verify_access_token(self):
        token = self.create_access(subject="user_42", role="admin")
        payload = self.verify(token, expected_type="access")
        self.assertEqual(payload["sub"], "user_42")
        self.assertEqual(payload["role"], "admin")
        self.assertEqual(payload["type"], "access")

    def test_expired_token_raises_401(self):
        from datetime import timedelta
        from app.core.exceptions import CustomException
        token = self.create_access(subject="user_1", expires_delta=timedelta(seconds=-1))
        with self.assertRaises(CustomException) as ctx:
            self.verify(token)
        self.assertEqual(ctx.exception.error_code, "TOKEN_EXPIRED")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_invalid_token_raises_401(self):
        from app.core.exceptions import CustomException
        with self.assertRaises(CustomException) as ctx:
            self.verify("this.is.not.a.valid.jwt")
        self.assertEqual(ctx.exception.error_code, "TOKEN_INVALID")

    def test_wrong_token_type_raises_401(self):
        from app.core.exceptions import CustomException
        # Create a refresh token but try to use it as access
        token = self.create_refresh(subject="user_99")
        with self.assertRaises(CustomException) as ctx:
            self.verify(token, expected_type="access")
        self.assertEqual(ctx.exception.error_code, "TOKEN_TYPE_MISMATCH")

    def test_refresh_token_verifies_as_refresh(self):
        token = self.create_refresh(subject="user_5")
        payload = self.verify(token, expected_type="refresh")
        self.assertEqual(payload["sub"], "user_5")
        self.assertEqual(payload["type"], "refresh")


# ======================================================================= #
# Security — Input Sanitizer                                               #
# ======================================================================= #

class TestSanitizer(unittest.TestCase):

    def setUp(self):
        from app.core.sanitizer import sanitize_string, sanitize_dict, InputSanitizationMixin
        self.sanitize_string = sanitize_string
        self.sanitize_dict = sanitize_dict
        self.mixin = InputSanitizationMixin

    def test_strips_html_tags(self):
        result = self.sanitize_string("<script>alert('xss')</script>Hello")
        self.assertNotIn("<script>", result)
        self.assertIn("Hello", result)

    def test_strips_javascript_protocol(self):
        result = self.sanitize_string("javascript:evil()")
        self.assertNotIn("javascript:", result)

    def test_strips_whitespace(self):
        result = self.sanitize_string("  hello world  ")
        self.assertEqual(result, "hello world")

    def test_truncates_to_max_length(self):
        result = self.sanitize_string("A" * 3000, max_length=100)
        self.assertEqual(len(result), 100)

    def test_sanitize_dict_recursively(self):
        data = {
            "name": "  <b>Bob</b>  ",
            "nested": {"bio": "<em>hacker</em>"},
            "count": 42,         # Non-string untouched
        }
        result = self.sanitize_dict(data)
        self.assertNotIn("<b>", result["name"])
        self.assertNotIn("<em>", result["nested"]["bio"])
        self.assertEqual(result["count"], 42)

    def test_pydantic_mixin_sanitizes_inputs(self):
        from pydantic import BaseModel

        class MyRequest(self.mixin, BaseModel):
            name: str
            description: str

        req = MyRequest(name="  <h1>Attack</h1>  ", description="  safe  ")
        self.assertNotIn("<h1>", req.name)
        self.assertEqual(req.description, "safe")


# ======================================================================= #
# Observability — Tracing                                                  #
# ======================================================================= #

class TestTracing(unittest.TestCase):

    def setUp(self):
        from app.observability.tracing import start_trace, get_trace_id, end_trace, get_or_create_trace_id
        self.start = start_trace
        self.get = get_trace_id
        self.end = end_trace
        self.get_or_create = get_or_create_trace_id

    def test_start_generates_uuid(self):
        tid = self.start()
        self.assertIsNotNone(tid)
        self.assertGreater(len(tid), 10)

    def test_get_returns_active_trace(self):
        tid = self.start("trace-abc-123")
        self.assertEqual(self.get(), "trace-abc-123")

    def test_end_clears_trace(self):
        self.start("trace-xyz")
        self.end()
        self.assertIsNone(self.get())

    def test_get_or_create_reuses_incoming(self):
        tid = self.get_or_create("existing-trace-id")
        self.assertEqual(tid, "existing-trace-id")

    def test_get_or_create_generates_when_none(self):
        tid = self.get_or_create(None)
        self.assertIsNotNone(tid)

    def test_get_or_create_rejects_oversized_incoming(self):
        # A 100-char "trace ID" is suspicious — should generate fresh
        tid = self.get_or_create("X" * 100)
        self.assertNotEqual(tid, "X" * 100)


# ======================================================================= #
# Observability — Metrics                                                  #
# ======================================================================= #

class TestMetrics(unittest.TestCase):

    def setUp(self):
        from app.observability.metrics import MetricsCollector
        self.collector = MetricsCollector.instance()
        self.collector.reset()

    def test_increment_and_read(self):
        self.collector.increment("requests_total")
        self.collector.increment("requests_total")
        self.assertEqual(self.collector.get_counter("requests_total"), 2)

    def test_increment_by_n(self):
        self.collector.increment("pipeline_executions_total", by=5)
        self.assertEqual(self.collector.get_counter("pipeline_executions_total"), 5)

    def test_latency_summary(self):
        for ms in [10.0, 20.0, 30.0, 100.0, 200.0]:
            self.collector.record_latency("request_latency_ms", ms)
        summary = self.collector.get_latency_summary("request_latency_ms")
        self.assertEqual(summary["count"], 5)
        self.assertGreater(summary["avg_ms"], 0)
        self.assertGreaterEqual(summary["max_ms"], 200.0)

    def test_snapshot_contains_counters_and_latencies(self):
        self.collector.increment("requests_total", 3)
        self.collector.record_latency("pipeline_latency_ms", 55.0)
        snap = self.collector.get_snapshot()
        self.assertIn("counters", snap)
        self.assertIn("latencies", snap)
        self.assertEqual(snap["counters"]["requests_total"], 3)
        self.assertIn("pipeline_latency_ms", snap["latencies"])

    def test_unrecognised_counter_returns_zero(self):
        self.assertEqual(self.collector.get_counter("nonexistent_metric"), 0)


# ======================================================================= #
# Observability — Logging trace_id injection                               #
# ======================================================================= #

class TestLoggingTraceInjection(unittest.TestCase):

    def test_log_record_contains_trace_id(self):
        import logging
        import json
        import io
        from app.core.logging import JSONFormatter
        from app.observability.tracing import start_trace, end_trace

        # Set up an in-memory log handler
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())

        logger = logging.getLogger("test.trace_inject")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Start a trace and emit a log
        trace_id = start_trace("test-trace-999")
        logger.info("Test message with trace")
        end_trace()

        # Parse the captured log output
        output = stream.getvalue().strip()
        record = json.loads(output)
        self.assertEqual(record.get("trace_id"), "test-trace-999")
        self.assertEqual(record.get("message"), "Test message with trace")


# ======================================================================= #
# Runner                                                                   #
# ======================================================================= #

if __name__ == "__main__":
    print("=" * 70)
    print("DeciFlow AI — Security + Observability Layer Tests")
    print("=" * 70)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
