"""
test_e2e_pipeline.py
---------------------
End-to-end pipeline integration test.
Tests the full flow:
  Raw Input → DataService → FeatureService → InsightService
           → PredictionService → DecisionService (+ DecisionIntelligenceEngine)
           → SimulationService → WorkflowEngine (async)

Run with: python test_e2e_pipeline.py
"""

import sys
import os
import asyncio
import unittest

# Replace hardcoded Windows path with dynamic path resolution
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend"))
sys.path.insert(0, backend_path)
os.environ["SECRET_KEY"] = "test-secret-key-safe-for-unit-tests-only-abc123"
os.environ["ENVIRONMENT"] = "development"


# ======================================================================= #
# Stage 1 — DataService                                                   #
# ======================================================================= #

class TestDataService(unittest.TestCase):
    def setUp(self):
        from app.services.data_service import DataService
        self.svc = DataService()

    def test_normal_payload(self):
        result = self.svc.process_raw_data("test", {"revenue": 1000, "users": 50})
        self.assertFalse(result["_fallback"])
        self.assertEqual(result["record_count"], 2)
        self.assertIn("revenue", result["fields"])

    def test_empty_payload_fallback(self):
        result = self.svc.process_raw_data("test", {})
        self.assertTrue(result["_fallback"])
        self.assertEqual(result["record_count"], 0)

    def test_none_payload_fallback(self):
        result = self.svc.process_raw_data("test", None)
        self.assertTrue(result["_fallback"])

    def test_string_values_stripped(self):
        result = self.svc.process_raw_data("test", {"name": "  Alice  "})
        self.assertEqual(result["raw"]["name"], "Alice")


# ======================================================================= #
# Stage 2 — FeatureService                                                #
# ======================================================================= #

class TestFeatureService(unittest.TestCase):
    def setUp(self):
        from app.services.feature_service import FeatureService
        self.svc = FeatureService()

    def test_typed_feature_extraction(self):
        processed = {"raw": {"revenue": 1000.0, "active": True, "region": "APAC"}, "_fallback": False}
        result = self.svc.extract_features(processed)
        self.assertFalse(result["_fallback"])
        self.assertIn("revenue", result["numeric"])
        self.assertIn("active", result["boolean"])
        self.assertIn("region", result["text"])

    def test_fallback_data_returns_fallback(self):
        result = self.svc.extract_features({"raw": {}, "_fallback": True})
        self.assertTrue(result["_fallback"])
        self.assertEqual(result["feature_count"], 0)


# ======================================================================= #
# Stage 3 — InsightService                                                #
# ======================================================================= #

class TestInsightService(unittest.TestCase):
    def setUp(self):
        from app.services.insight_service import InsightService
        self.svc = InsightService()

    def test_generates_insights_from_features(self):
        features = {
            "numeric": {"revenue": 500.0, "churn_rate": 0.1},
            "boolean": {}, "text": {}, "feature_count": 2, "_fallback": False
        }
        result = self.svc.generate_insights(features)
        self.assertFalse(result["_fallback"])
        self.assertGreater(result["confidence"], 0.0)
        self.assertIn(result["top_signal"], ["revenue", "churn_rate"])

    def test_anomaly_detection(self):
        features = {
            "numeric": {"spike": 9999.0},
            "boolean": {}, "text": {}, "feature_count": 1, "_fallback": False
        }
        result = self.svc.generate_insights(features)
        self.assertTrue(result["anomaly_detected"])

    def test_empty_features_fallback(self):
        result = self.svc.generate_insights({"feature_count": 0, "_fallback": True})
        self.assertTrue(result["_fallback"])
        self.assertEqual(result["confidence"], 0.0)


# ======================================================================= #
# Stage 4 — PredictionService                                             #
# ======================================================================= #

class TestPredictionService(unittest.TestCase):
    def setUp(self):
        from app.services.prediction_service import PredictionService
        self.svc = PredictionService()

    def test_derives_score_from_confidence(self):
        insights = {"confidence": 0.9, "anomaly_detected": False, "_fallback": False}
        result = self.svc.predict(insights)
        self.assertFalse(result["_fallback"])
        self.assertAlmostEqual(result["prediction_score"], 0.9, places=1)

    def test_anomaly_reduces_score(self):
        insights = {"confidence": 0.9, "anomaly_detected": True, "_fallback": False}
        result = self.svc.predict(insights)
        self.assertLess(result["prediction_score"], 0.9)

    def test_fallback_input_returns_neutral(self):
        result = self.svc.predict({"_fallback": True})
        self.assertTrue(result["_fallback"])
        self.assertEqual(result["prediction_score"], 0.5)


# ======================================================================= #
# Stage 5 — DecisionIntelligenceEngine + DecisionService                  #
# ======================================================================= #

class TestDecisionPipeline(unittest.TestCase):
    def setUp(self):
        from app.decision_engine.modules.generator import DefaultGenerator
        from app.decision_engine.modules.scorer import DefaultScorer
        from app.decision_engine.modules.ranker import DefaultRanker
        from app.decision_engine.modules.constraints import DefaultConstraintEngine
        from app.decision_engine.modules.explainer import DefaultExplainer
        from app.decision_engine.engine import DecisionIntelligenceEngine
        from app.services.decision_service import DecisionService

        engine = DecisionIntelligenceEngine(
            generator=DefaultGenerator(),
            scorer=DefaultScorer(),
            ranker=DefaultRanker(),
            constraint_engine=DefaultConstraintEngine(),
            explainer=DefaultExplainer(),
        )
        self.svc = DecisionService(engine=engine)

    def test_full_decision(self):
        context = {
            "session_id": "test-session-01",
            "insights": {"context": "revenue_up", "confidence": 0.8, "metrics_snapshot": {"revenue": 500.0}},
            "predictions": {"prediction_score": 0.8, "confidence": 0.8, "probabilities": {"positive": 0.8, "negative": 0.2}},
        }
        result = self.svc.orchestrate_decision(context)
        self.assertFalse(result["_fallback"])
        self.assertIn(result["action"], ["REDUCE_PRICE", "HOLD"])
        self.assertGreater(result["score"], 0.0)
        self.assertIsInstance(result["explanation"], str)
        self.assertGreater(len(result["explanation"]), 10)

    def test_empty_context_triggers_fallback(self):
        result = self.svc.orchestrate_decision({})
        self.assertTrue(result["_fallback"])
        self.assertEqual(result["action"], "NO_ACTION")

    def test_fallback_insights_still_works(self):
        context = {
            "session_id": "test-fallback",
            "insights": {"context": "no_context", "confidence": 0.0, "metrics_snapshot": {}},
            "predictions": {"prediction_score": 0.5, "confidence": 0.0},
        }
        # Engine should return fallback (no context = no actions generated)
        result = self.svc.orchestrate_decision(context)
        self.assertIsNotNone(result["action"])  # Never crashes


# ======================================================================= #
# Stage 6 — SimulationService                                             #
# ======================================================================= #

class TestSimulationService(unittest.TestCase):
    def setUp(self):
        from app.services.simulation_service import SimulationService
        self.svc = SimulationService()

    def test_real_roi_calculation(self):
        decision = {"action": "REDUCE_PRICE", "score": 0.8, "confidence": 0.9, "_fallback": False}
        result = self.svc.simulate(decision)
        self.assertFalse(result["_fallback"])
        self.assertGreater(result["projected_roi"], 0.0)
        self.assertIn(result["risk_level"], ["low", "medium", "high"])

    def test_none_decision_fallback(self):
        result = self.svc.simulate(None)
        self.assertTrue(result["_fallback"])
        self.assertEqual(result["projected_roi"], 0.0)

    def test_low_confidence_high_risk(self):
        decision = {"action": "APPROVE", "score": 0.3, "confidence": 0.3}
        result = self.svc.simulate(decision)
        self.assertEqual(result["risk_level"], "high")


# ======================================================================= #
# Full WorkflowEngine E2E (async)                                         #
# ======================================================================= #

class TestWorkflowEngineE2E(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        from app.decision_engine.modules.generator import DefaultGenerator
        from app.decision_engine.modules.scorer import DefaultScorer
        from app.decision_engine.modules.ranker import DefaultRanker
        from app.decision_engine.modules.constraints import DefaultConstraintEngine
        from app.decision_engine.modules.explainer import DefaultExplainer
        from app.decision_engine.engine import DecisionIntelligenceEngine
        from app.services.data_service import DataService
        from app.services.feature_service import FeatureService
        from app.services.insight_service import InsightService
        from app.services.prediction_service import PredictionService
        from app.services.decision_service import DecisionService
        from app.services.simulation_service import SimulationService
        from app.orchestration.engine import WorkflowEngine

        die = DecisionIntelligenceEngine(
            generator=DefaultGenerator(), scorer=DefaultScorer(),
            ranker=DefaultRanker(), constraint_engine=DefaultConstraintEngine(),
            explainer=DefaultExplainer(),
        )
        self.engine = WorkflowEngine(
            data_svc=DataService(),
            feature_svc=FeatureService(),
            insight_svc=InsightService(),
            prediction_svc=PredictionService(),
            decision_svc=DecisionService(engine=die),
            simulation_svc=SimulationService(),
        )

    async def test_full_pipeline_normal_input(self):
        state = await self.engine.execute_pipeline(
            session_id="e2e-test-001",
            payload={"revenue": 1500.0, "users": 200, "churn_rate": 0.05, "region": "APAC"},
        )
        self.assertIsNotNone(state.decisions)
        self.assertIsNotNone(state.simulation)
        self.assertIn(state.decisions["action"], ["REDUCE_PRICE", "HOLD", "NO_ACTION"])
        self.assertIsNotNone(state.simulation.get("projected_roi"))

    async def test_full_pipeline_empty_payload_doesnt_crash(self):
        state = await self.engine.execute_pipeline(
            session_id="e2e-test-002",
            payload={},
        )
        # Must not raise — system must always return a complete state
        self.assertIsNotNone(state.decisions)
        self.assertIn("action", state.decisions)
        # Decision can be NO_ACTION (full fallback) or a real action (degraded but alive)
        self.assertIsInstance(state.decisions["action"], str)
        self.assertIsNotNone(state.simulation)


    async def test_full_pipeline_output_structure(self):
        state = await self.engine.execute_pipeline(
            session_id="e2e-test-003",
            payload={"profit_margin": 0.3, "growth_rate": 12.5},
        )
        self.assertIn("action", state.decisions)
        self.assertIn("explanation", state.decisions)
        self.assertIn("projected_roi", state.simulation)
        self.assertIn("risk_level", state.simulation)


# ======================================================================= #
# Runner                                                                   #
# ======================================================================= #

if __name__ == "__main__":
    print("=" * 70)
    print("DeciFlow AI — Full End-to-End Pipeline Integration Test")
    print("=" * 70)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
