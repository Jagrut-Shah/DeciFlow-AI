"""Pipeline status tracking verification tests."""
import asyncio
import sys
import logging

logging.disable(logging.CRITICAL)
sys.path.insert(0, ".")

from app.orchestration.models import PipelineState, PipelineStatus, ExecutionMode
from app.core.result_store import ResultStore

results = []

def record(ok, msg):
    icon = "[PASS]" if ok else "[FAIL]"
    print(f"{icon} {msg}")
    results.append(ok)


async def run():
    # T1: Default status is PENDING
    s = PipelineState(session_id="t1")
    record(
        s.status == PipelineStatus.PENDING
        and s.started_at is None
        and s.completed_at is None,
        "T1 - Default status=PENDING, no timestamps"
    )

    # T2: Happy-path -> COMPLETED + timestamps
    from app.core.dependencies import _build_result_store, _build_workflow_engine
    _build_result_store.cache_clear()
    _build_workflow_engine.cache_clear()

    engine = _build_workflow_engine()
    state = await engine.execute_pipeline("sess-happy", {"revenue": 5000}, ExecutionMode.RESILIENT)

    record(
        state.status == PipelineStatus.COMPLETED
        and state.started_at is not None
        and state.completed_at is not None
        and state.completed_at >= state.started_at
        and state.duration_seconds is not None
        and state.duration_seconds >= 0,
        f"T2 - COMPLETED: started_at set, completed_at set, duration={state.duration_seconds:.3f}s"
    )

    # T3: ResultStore holds COMPLETED state
    stored = await engine._result_store.get_result("sess-happy")
    record(
        stored is not None and stored.status == PipelineStatus.COMPLETED,
        f"T3 - ResultStore.status={stored.status.value if stored else 'MISSING'}"
    )

    # T4: RUNNING snapshot saved BEFORE steps, COMPLETED saved AFTER
    from app.orchestration.engine import WorkflowEngine
    from app.services.data_service import DataService
    from app.services.feature_service import FeatureService
    from app.services.insight_service import InsightService
    from app.services.prediction_service import PredictionService
    from app.services.decision_service import DecisionService
    from app.services.simulation_service import SimulationService
    from app.decision_engine.engine import DecisionIntelligenceEngine
    from app.decision_engine.modules.generator import DefaultGenerator
    from app.decision_engine.modules.scorer import DefaultScorer
    from app.decision_engine.modules.ranker import DefaultRanker
    from app.decision_engine.modules.constraints import DefaultConstraintEngine
    from app.decision_engine.modules.explainer import DefaultExplainer

    snapshots = []

    class CapturingStore(ResultStore):
        async def save_result(self, sid, st):
            snapshots.append(st.status.value)
            await super().save_result(sid, st)

    die = DecisionIntelligenceEngine(
        generator=DefaultGenerator(), scorer=DefaultScorer(), ranker=DefaultRanker(),
        constraint_engine=DefaultConstraintEngine(), explainer=DefaultExplainer(),
    )
    eng2 = WorkflowEngine(
        data_svc=DataService(), feature_svc=FeatureService(),
        insight_svc=InsightService(), prediction_svc=PredictionService(),
        decision_svc=DecisionService(engine=die), simulation_svc=SimulationService(),
        result_store=CapturingStore(),
    )
    await eng2.execute_pipeline("sess-capture", {"revenue": 1000}, ExecutionMode.RESILIENT)

    record(
        len(snapshots) >= 2 and snapshots[0] == "RUNNING" and snapshots[-1] == "COMPLETED",
        f"T4 - Store snapshots sequence: {snapshots}"
    )

    # T5: Exception path -> FAILED in store with error metadata
    class AlwaysBoom:
        def extract_features(self, d):
            raise RuntimeError("intentional boom")

    fail_store = ResultStore()
    eng_fail = WorkflowEngine(
        data_svc=DataService(), feature_svc=AlwaysBoom(),
        insight_svc=InsightService(), prediction_svc=PredictionService(),
        decision_svc=DecisionService(engine=die), simulation_svc=SimulationService(),
        result_store=fail_store,
    )
    try:
        await eng_fail.execute_pipeline("sess-fail", {"x": 1}, ExecutionMode.STRICT)
    except RuntimeError:
        pass

    failed = await fail_store.get_result("sess-fail")
    record(
        failed is not None
        and failed.status == PipelineStatus.FAILED
        and failed.completed_at is not None
        and "error" in failed.metadata
        and "error_type" in failed.metadata,
        f"T5 - FAILED: status={failed.status.value if failed else None}, "
        f"error={failed.metadata.get('error') if failed else None}"
    )

    # T6: RESILIENT mode completes despite failure (no exception raised) -> COMPLETED
    resilient_store = ResultStore()
    eng_r = WorkflowEngine(
        data_svc=DataService(), feature_svc=AlwaysBoom(),
        insight_svc=InsightService(), prediction_svc=PredictionService(),
        decision_svc=DecisionService(engine=die), simulation_svc=SimulationService(),
        result_store=resilient_store,
    )
    resilient_state = await eng_r.execute_pipeline("sess-resilient", {"x": 1}, ExecutionMode.RESILIENT)
    resilient_stored = await resilient_store.get_result("sess-resilient")
    record(
        resilient_state.status == PipelineStatus.COMPLETED
        and resilient_stored is not None
        and resilient_stored.status == PipelineStatus.COMPLETED,
        f"T6 - RESILIENT with broken step: status={resilient_state.status.value}"
    )

    # T7: duration_seconds is a float
    record(
        isinstance(state.duration_seconds, float) and state.duration_seconds >= 0,
        f"T7 - duration_seconds={state.duration_seconds}"
    )

    # T8: metadata carries mode value
    record(
        state.metadata.get("mode") == "RESILIENT",
        f"T8 - metadata.mode={state.metadata.get('mode')}"
    )

    # Summary
    passed = sum(results)
    total = len(results)
    print()
    print(f"=== {passed}/{total} PASSED ===")
    sys.exit(0 if passed == total else 1)


asyncio.run(run())
