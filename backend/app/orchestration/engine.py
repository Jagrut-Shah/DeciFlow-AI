import logging
from datetime import datetime, timezone
from typing import Optional

from app.domain.interfaces.data_service import IDataService
from app.domain.interfaces.feature_service import IFeatureService
from app.domain.interfaces.insight_service import IInsightService
from app.domain.interfaces.prediction_service import IPredictionService
from app.domain.interfaces.decision_service import IDecisionService
from app.domain.interfaces.simulation_service import ISimulationService

from app.orchestration.models import PipelineState, PipelineStatus, ExecutionMode
from app.orchestration.pipeline import PipelineStep, _execute_step
from app.core.result_store import ResultStore

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


class WorkflowEngine:
    def __init__(
        self,
        data_svc: IDataService,
        feature_svc: IFeatureService,
        insight_svc: IInsightService,
        prediction_svc: IPredictionService,
        decision_svc: IDecisionService,
        simulation_svc: ISimulationService,
        result_store: Optional[ResultStore] = None,
        default_mode: ExecutionMode = ExecutionMode.STRICT,
    ):
        self.data = data_svc
        self.feature = feature_svc
        self.insight = insight_svc
        self.prediction = prediction_svc
        self.decision = decision_svc
        self.simulation = simulation_svc
        self._result_store = result_store
        self.default_mode = default_mode

    # ── Private helpers ───────────────────────────────────────────────────────

    async def _persist(self, state: PipelineState) -> None:
        """Save current state snapshot into ResultStore (no-op if not wired)."""
        if self._result_store is not None:
            await self._result_store.save_result(state.session_id, state)

    # ── Public API ────────────────────────────────────────────────────────────

    async def execute_pipeline(
        self,
        session_id: str,
        payload: dict,
        mode: Optional[ExecutionMode] = None,
    ) -> PipelineState:
        # Use provided mode or fall back to engine default
        active_mode = mode or self.default_mode
        
        # ── Initialise state (PENDING → RUNNING) ──────────────────────────────
        state = PipelineState(session_id=session_id)
        state.raw_data = payload
        state.status = PipelineStatus.RUNNING
        state.started_at = _utcnow()
        state.metadata["mode"] = active_mode.value

        logger.info(
            "WorkflowEngine: pipeline RUNNING",
            extra={"session_id": session_id, "mode": active_mode.value,
                   "started_at": state.started_at.isoformat()},
        )

        # Persist the RUNNING snapshot immediately so callers can poll status
        await self._persist(state)

        # ── Execute steps ─────────────────────────────────────────────────────
        
        async def _run_data(data):
            return await self.data.process_raw_data("workflow_engine", data)
            
        async def _run_decision(predictions):
            return await self.decision.orchestrate_decision({
                "session_id": state.session_id,
                "insights": state.insights,
                "predictions": predictions,
            })

        steps = [
            PipelineStep(
                name="DataIngestion",
                func=_run_data,
                input_key="raw_data",
                output_key="raw_data",
            ),
            PipelineStep(
                name="FeatureEngineering",
                func=self.feature.extract_features,
                input_key="raw_data",
                output_key="features",
            ),
            PipelineStep(
                name="InsightGeneration",
                func=self.insight.generate_insights,
                input_key="features",
                output_key="insights",
            ),
            PipelineStep(
                name="Prediction",
                func=self.prediction.predict,
                input_key="insights",
                output_key="predictions",
            ),
            PipelineStep(
                name="Decision",
                func=_run_decision,
                input_key="predictions",
                output_key="decisions",
            ),
            PipelineStep(
                name="Simulation",
                func=self.simulation.simulate,
                input_key="decisions",
                output_key="simulation",
            ),
        ]

        try:
            for step in steps:
                state = await _execute_step(step, state, active_mode)

        except Exception as exc:
            # ── FAILED ────────────────────────────────────────────────────────
            state.status = PipelineStatus.FAILED
            state.completed_at = _utcnow()
            state.metadata["error"] = str(exc)
            state.metadata["error_type"] = type(exc).__name__

            logger.error(
                "WorkflowEngine: pipeline FAILED",
                extra={
                    "session_id": session_id,
                    "error": str(exc),
                    "duration_s": state.duration_seconds,
                },
                exc_info=True,
            )

            # Persist FAILED state so callers can observe the failure
            await self._persist(state)
            raise  # re-raise so STRICT mode callers see the error

        # ── COMPLETED ─────────────────────────────────────────────────────────
        state.status = PipelineStatus.COMPLETED
        state.completed_at = _utcnow()

        logger.info(
            "WorkflowEngine: pipeline COMPLETED",
            extra={
                "session_id": session_id,
                "duration_s": state.duration_seconds,
                "status": state.status.value,
            },
        )

        # Persist final COMPLETED state
        await self._persist(state)
        return state
