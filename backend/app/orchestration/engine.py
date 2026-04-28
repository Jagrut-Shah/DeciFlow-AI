import logging
import asyncio
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
            try:
                # Set a reasonable timeout for persistence to prevent I/O blocking
                await asyncio.wait_for(self._result_store.save_result(state.session_id, state), timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning(f"WorkflowEngine: Persistence timed out for session {state.session_id}")
            except Exception as e:
                logger.error(f"WorkflowEngine: Persistence failed: {e}")

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

        async def _run_insights(features):
            # Combine extracted features with raw data metrics for rich insights
            return await self.insight.generate_insights({
                "features": features,
                "raw_data": state.raw_data,
                "mode": active_mode.name
            })
            
        async def _run_prediction(features):
            # NEW: Run prediction from features/raw_data directly in parallel with insights
            return await self.prediction.predict({
                "features": features,
                "raw_data": state.raw_data,
                "mode": active_mode.name
            })

        async def _run_decision(predictions):
            return await self.decision.orchestrate_decision({
                "session_id": state.session_id,
                "insights": state.insights,
                "predictions": predictions,
                "mode": active_mode.name
            })

        async def _core_execution():
            nonlocal state
            # Step 1: Data Ingestion
            step_data = PipelineStep(
                name="DataIngestion",
                func=_run_data,
                input_key="raw_data",
                output_key="raw_data",
            )
            state.metadata["current_step"] = "DataIngestion"
            state = await _execute_step(step_data, state, active_mode)
            state.steps_completed.append("DataIngestion")
            await self._persist(state)

            # Step 2: Feature Engineering
            step_feature = PipelineStep(
                name="FeatureEngineering",
                func=self.feature.extract_features,
                input_key="raw_data",
                output_key="features",
            )
            state.metadata["current_step"] = "FeatureEngineering"
            state = await _execute_step(step_feature, state, active_mode)
            state.steps_completed.append("FeatureEngineering")
            await self._persist(state)

            # Step 3 & 4: Insight Generation & Prediction (PARALLEL)
            # Execute both in parallel as independent coroutines with a dedicated timeout
            state.metadata["current_step"] = "InsightAndPrediction"
            
            try:
                # Run parallel steps with a 60s limit (should be plenty for LLM calls)
                results = await asyncio.wait_for(
                    asyncio.gather(
                        _run_insights(state.features),
                        _run_prediction(state.features),
                        return_exceptions=True
                    ),
                    timeout=60.0
                )
                
                # Process results sequentially to update state safely
                if isinstance(results[0], Exception):
                    logger.error(f"WorkflowEngine: InsightGeneration failed: {results[0]}")
                    state.insights = {"status": "error", "insights": [], "main_insight": "Insight engine encountered a transient error."}
                else:
                    state.insights = results[0]
                    state.steps_completed.append("InsightGeneration")
                    
                if isinstance(results[1], Exception):
                    logger.error(f"WorkflowEngine: Prediction failed: {results[1]}")
                    state.predictions = {"status": "error", "predictions": [], "prediction_score": 0.5}
                else:
                    state.predictions = results[1]
                    state.steps_completed.append("Prediction")
                    
            except asyncio.TimeoutError:
                logger.error(f"WorkflowEngine: Parallel steps (Insight/Prediction) timed out")
                state.insights = state.insights or {"status": "timeout", "main_insight": "Analysis timed out. Please retry."}
                state.predictions = state.predictions or {"status": "timeout", "prediction_score": 0.5}

            # Persist now that both parallel steps are committed to state
            await self._persist(state)
            state.metadata["current_step"] = "Decision" # Prepare for next

            # Step 5: Decision
            step_decision = PipelineStep(
                name="Decision",
                func=_run_decision,
                input_key="predictions",
                output_key="decisions",
            )
            state.metadata["current_step"] = "Decision"
            state = await _execute_step(step_decision, state, active_mode)
            state.steps_completed.append("Decision")
            await self._persist(state)

            # Step 6: Simulation
            step_simulation = PipelineStep(
                name="Simulation",
                func=self.simulation.simulate,
                input_key="decisions",
                output_key="simulation",
            )
            state.metadata["current_step"] = "Simulation"
            state = await _execute_step(step_simulation, state, active_mode)
            state.steps_completed.append("Simulation")
            await self._persist(state)

        try:
            # Wrap entire execution in a global timeout (2 minutes)
            await asyncio.wait_for(_core_execution(), timeout=120)

        except asyncio.TimeoutError:
            state.status = PipelineStatus.FAILED
            state.completed_at = _utcnow()
            state.metadata["error"] = "Global Pipeline Timeout (120s exceeded)"
            logger.error(f"WorkflowEngine: Pipeline TIMEOUT for {session_id}")
            await self._persist(state)
            return state

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
            if active_mode == ExecutionMode.STRICT:
                raise
            return state

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

