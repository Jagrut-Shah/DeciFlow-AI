import os
import sys

# Use dynamic pathing to ensure portability across different development environments
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/app"))
orch_dir = os.path.join(base_dir, "orchestration")
os.makedirs(orch_dir, exist_ok=True)
os.makedirs(os.path.join(base_dir, "domain", "interfaces"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "services"), exist_ok=True)

# 1. Simulation Service
sim_interface_code = """from abc import ABC, abstractmethod
from typing import Any

class ISimulationService(ABC):
    @abstractmethod
    def simulate(self, decision: Any) -> Any: pass
"""
with open(os.path.join(base_dir, "domain", "interfaces", "simulation_service.py"), "w", encoding="utf-8") as f: f.write(sim_interface_code)

sim_service_code = """from typing import Any
from app.domain.interfaces.simulation_service import ISimulationService

class SimulationService(ISimulationService):
    def simulate(self, decision: Any) -> Any:
        return {"simulated": True, "projected_roi": 1.25, "decision": decision}
"""
with open(os.path.join(base_dir, "services", "simulation_service.py"), "w", encoding="utf-8") as f: f.write(sim_service_code)

# 2. Orchestration Models
models_code = """from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum

class ExecutionMode(str, Enum):
    STRICT = "STRICT"
    RESILIENT = "RESILIENT"

class PipelineState(BaseModel):
    session_id: str
    raw_data: Optional[Any] = None
    features: Optional[Any] = None
    insights: Optional[Any] = None
    predictions: Optional[Any] = None
    decisions: Optional[Any] = None
    simulation: Optional[Any] = None
    metadata: dict = {}
"""
with open(os.path.join(orch_dir, "models.py"), "w", encoding="utf-8") as f: f.write(models_code)
with open(os.path.join(orch_dir, "__init__.py"), "w", encoding="utf-8") as f: f.write("")

# 3. Pipeline Wrapper
pipeline_code = """import time
import logging
from typing import Callable, Any, Awaitable
from pydantic import BaseModel
from app.orchestration.models import PipelineState, ExecutionMode

logger = logging.getLogger(__name__)

class PipelineStep(BaseModel):
    name: str
    func: Callable[..., Any]
    input_key: str
    output_key: str

async def _execute_step(step: PipelineStep, state: PipelineState, mode: ExecutionMode) -> PipelineState:
    start_time = time.time()
    input_data = getattr(state, step.input_key)
    
    logger.info(f"[{state.session_id}] Executing step: {step.name}")
    
    try:
        # Check if function is async
        import inspect
        if inspect.iscoroutinefunction(step.func):
            output = await step.func(input_data)
        else:
            output = step.func(input_data)
            
        setattr(state, step.output_key, output)
        
        exec_time = time.time() - start_time
        logger.info(f"[{state.session_id}] {step.name} SUCCESS ({exec_time:.4f}s)")
        state.metadata[f"{step.name}_status"] = "SUCCESS"
        
    except Exception as e:
        exec_time = time.time() - start_time
        logger.error(f"[{state.session_id}] {step.name} FAILED: {str(e)} ({exec_time:.4f}s)")
        state.metadata[f"{step.name}_status"] = "FAILED"
        
        if mode == ExecutionMode.STRICT:
            raise RuntimeError(f"Pipeline failed at {step.name} strictly: {str(e)}")
        else:
            logger.warning(f"[{state.session_id}] RESILIENT MODE: Injecting fallback for {step.name}")
            setattr(state, step.output_key, {"error": str(e), "fallback": True})
            
    return state
"""
with open(os.path.join(orch_dir, "pipeline.py"), "w", encoding="utf-8") as f: f.write(pipeline_code)

# 4. Engine
engine_code = """import logging
from app.domain.interfaces.data_service import IDataService
from app.domain.interfaces.feature_service import IFeatureService
from app.domain.interfaces.insight_service import IInsightService
from app.domain.interfaces.prediction_service import IPredictionService
from app.domain.interfaces.decision_service import IDecisionService
from app.domain.interfaces.simulation_service import ISimulationService

from app.orchestration.models import PipelineState, ExecutionMode
from app.orchestration.pipeline import PipelineStep, _execute_step

logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(
        self,
        data_svc: IDataService,
        feature_svc: IFeatureService,
        insight_svc: IInsightService,
        prediction_svc: IPredictionService,
        decision_svc: IDecisionService,
        simulation_svc: ISimulationService
    ):
        self.data = data_svc
        self.feature = feature_svc
        self.insight = insight_svc
        self.prediction = prediction_svc
        self.decision = decision_svc
        self.simulation = simulation_svc

    async def execute_pipeline(self, session_id: str, payload: dict, mode: ExecutionMode = ExecutionMode.STRICT) -> PipelineState:
        logger.info(f"[{session_id}] Starting Pipeline Orchestration (Mode: {mode})")
        
        state = PipelineState(session_id=session_id)
        # Prime the state with inbound payload mapped to 'raw_data'
        # In a real scenario, data fetching might happen cleanly. For orchestration flow, we simulate payload as raw data
        state.raw_data = payload
        
        steps = [
            # Note: We bypass data fetching block directly if payload is passed, or simulate it. 
            # We map actual services dynamically. For interfaces returning non-awaitable right now, _execute_step handles both.
            PipelineStep(name="DataIngestion", func=self.data.get_data.__func__ if hasattr(self.data.get_data, '__func__') else self.data.get_data, input_key="raw_data", output_key="raw_data"),
            PipelineStep(name="FeatureEngineering", func=self.feature.extract_features.__func__ if hasattr(self.feature.extract_features, '__func__') else self.feature.extract_features, input_key="raw_data", output_key="features"),
            PipelineStep(name="InsightGeneration", func=self.insight.generate_insights.__func__ if hasattr(self.insight.generate_insights, '__func__') else self.insight.generate_insights, input_key="features", output_key="insights"),
            PipelineStep(name="Prediction", func=self.prediction.predict.__func__ if hasattr(self.prediction.predict, '__func__') else self.prediction.predict, input_key="insights", output_key="predictions"),
            PipelineStep(name="Decision", func=self.decision.orchestrate_decision.__func__ if hasattr(self.decision.orchestrate_decision, '__func__') else self.decision.orchestrate_decision, input_key="predictions", output_key="decisions"),
            PipelineStep(name="Simulation", func=self.simulation.simulate.__func__ if hasattr(self.simulation.simulate, '__func__') else self.simulation.simulate, input_key="decisions", output_key="simulation")
        ]
        
        for step in steps:
            state = await _execute_step(step, state, mode)
            
        logger.info(f"[{session_id}] Pipeline Orchestration Completed.")
        return state
"""
with open(os.path.join(orch_dir, "engine.py"), "w", encoding="utf-8") as f: f.write(engine_code)

print("Orchestration engine successfully built.")
