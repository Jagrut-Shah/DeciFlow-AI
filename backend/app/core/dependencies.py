"""
Dependency Injection — Core dependencies for FastAPI route handlers.
"""

import functools
from fastapi import Request, Depends
from typing import Optional

from app.core.config import settings
from app.core.exceptions import CustomException
from app.core.security import verify_token

# --- Service imports ---
from app.domain.interfaces.data_service import IDataService
from app.services.data_service import DataService

from app.domain.interfaces.feature_service import IFeatureService
from app.services.feature_service import FeatureService

from app.domain.interfaces.insight_service import IInsightService
from app.services.insight_service import InsightService

from app.domain.interfaces.prediction_service import IPredictionService
from app.services.prediction_service import PredictionService

from app.domain.interfaces.agent_service import IAgentService
from app.services.agent_service import AgentService

from app.domain.interfaces.decision_service import IDecisionService
from app.services.decision_service import DecisionService

from app.domain.interfaces.llm_interface import ILLMService
from app.infrastructure.ai.vertex_ai import GeminiService

from app.domain.interfaces.simulation_service import ISimulationService
from app.services.simulation_service import SimulationService

from app.orchestration.engine import WorkflowEngine
from app.orchestration.models import ExecutionMode

from app.domain.interfaces.repositories import IUserRepository, IDatasetRepository, IMetricsRepository
from app.infrastructure.data.bigquery_adapter import BigQueryAdapter
from app.infrastructure.data.storage_adapter import StorageAdapter
from app.infrastructure.repositories.implementations import UserRepository, DatasetRepository, MetricsRepository

from app.domain.interfaces.queue import ITaskQueue, ITaskRegistry
from app.infrastructure.queue.registry import TaskRegistry
from app.infrastructure.queue.memory_queue import MemoryQueue
from app.workers.pipeline_worker import PipelineWorker

# Decision Intelligence Engine
from app.decision_engine.engine import DecisionIntelligenceEngine
from app.decision_engine.modules.generator import DefaultGenerator
from app.decision_engine.modules.scorer import DefaultScorer
from app.decision_engine.modules.ranker import DefaultRanker
from app.decision_engine.modules.constraints import DefaultConstraintEngine
from app.decision_engine.modules.explainer import DefaultExplainer
from app.decision_engine.advanced.adaptive_learning import AdaptiveLearning

from app.core.result_store import ResultStore


# =========================================================================== #
# Module-level Singletons                                                      #
# (Shared across all requests — DI injects the same instance)                 #
# =========================================================================== #

@functools.lru_cache(maxsize=1)
def _build_decision_intelligence_engine() -> DecisionIntelligenceEngine:
    """Build and cache the DecisionIntelligenceEngine singleton."""
    return DecisionIntelligenceEngine(
        generator=DefaultGenerator(),
        scorer=DefaultScorer(),
        ranker=DefaultRanker(),
        constraint_engine=DefaultConstraintEngine(),
        explainer=DefaultExplainer(),
        adaptive_learning=AdaptiveLearning(),
    )


@functools.lru_cache(maxsize=1)
def _build_result_store() -> Optional[ResultStore]:
    """Build and cache the ResultStore singleton or return None if disabled."""
    if not settings.RESULT_STORE_ENABLED:
        return None
    return ResultStore()


@functools.lru_cache(maxsize=1)
def _build_workflow_engine() -> WorkflowEngine:
    """Build and cache the WorkflowEngine singleton with all service dependencies."""
    data_svc = DataService()
    feature_svc = FeatureService()
    insight_svc = InsightService()
    prediction_svc = PredictionService()
    die = _build_decision_intelligence_engine()
    decision_svc = DecisionService(engine=die)
    simulation_svc = SimulationService()

    return WorkflowEngine(
        data_svc=data_svc,
        feature_svc=feature_svc,
        insight_svc=insight_svc,
        prediction_svc=prediction_svc,
        decision_svc=decision_svc,
        simulation_svc=simulation_svc,
        result_store=_build_result_store(),
        default_mode=ExecutionMode(settings.PIPELINE_MODE),
    )


# =========================================================================== #
# Service Factories                                                            #
# =========================================================================== #

def get_data_service() -> IDataService:
    return DataService()

def get_feature_service() -> IFeatureService:
    return FeatureService()

def get_insight_service() -> IInsightService:
    return InsightService()

def get_prediction_service() -> IPredictionService:
    return PredictionService()

def get_agent_service() -> IAgentService:
    return AgentService()

def get_llm_service() -> ILLMService:
    return GeminiService()

def get_bigquery_adapter() -> BigQueryAdapter:
    return BigQueryAdapter(project_id="deciflow-prod")

def get_storage_adapter() -> StorageAdapter:
    return StorageAdapter(bucket_name="deciflow-data-lake")

def get_user_repository(bq: BigQueryAdapter = Depends(get_bigquery_adapter)) -> IUserRepository:
    return UserRepository(db_adapter=bq)

def get_dataset_repository(
    storage: StorageAdapter = Depends(get_storage_adapter),
    bq: BigQueryAdapter = Depends(get_bigquery_adapter),
) -> IDatasetRepository:
    return DatasetRepository(storage_adapter=storage, bq_adapter=bq)

def get_metrics_repository(bq: BigQueryAdapter = Depends(get_bigquery_adapter)) -> IMetricsRepository:
    return MetricsRepository(db_adapter=bq)

def get_decision_engine() -> DecisionIntelligenceEngine:
    """Returns the cached DecisionIntelligenceEngine singleton."""
    return _build_decision_intelligence_engine()

def get_decision_service(
    engine: DecisionIntelligenceEngine = Depends(get_decision_engine),
) -> IDecisionService:
    return DecisionService(engine=engine)

def get_simulation_service() -> ISimulationService:
    return SimulationService()

def get_workflow_engine() -> WorkflowEngine:
    """Returns the cached WorkflowEngine singleton."""
    return _build_workflow_engine()


def get_result_store() -> Optional[ResultStore]:
    """Returns the cached ResultStore singleton or None if disabled."""
    return _build_result_store()


# =========================================================================== #
# Queue & Worker Factories (Singletons)                                        #
# =========================================================================== #

_task_registry_instance = TaskRegistry()
_task_queue_instance = MemoryQueue(registry=_task_registry_instance)

def get_task_registry() -> ITaskRegistry:
    return _task_registry_instance

def get_task_queue() -> ITaskQueue:
    return _task_queue_instance

def get_pipeline_worker() -> PipelineWorker:
    """Returns a PipelineWorker wired to the singleton WorkflowEngine."""
    return PipelineWorker(_build_workflow_engine())


# =========================================================================== #
# Auth & Security Dependencies                                                 #
# =========================================================================== #

def get_db():
    """Database session placeholder — swap in SQLAlchemy/async session here."""
    yield None


def get_current_user(request: Request) -> dict:
    """
    Extracts and validates the Bearer JWT from the Authorization header.
    Returns the decoded token payload.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise CustomException(
            message="Authorization header missing or malformed. Use 'Bearer <token>'.",
            status_code=401,
            error_code="UNAUTHORIZED",
        )
    token = auth_header.split(" ", 1)[1]
    return verify_token(token, expected_type="access")


def require_role(required_role: str):
    """Factory that returns a FastAPI dependency enforcing a specific role."""
    def role_checker(payload: dict = Depends(get_current_user)) -> dict:
        user_role = payload.get("role", "user")
        if user_role != required_role:
            raise CustomException(
                message=f"Access denied. Required role: '{required_role}', your role: '{user_role}'.",
                status_code=403,
                error_code="FORBIDDEN",
            )
        return payload
    return role_checker


def get_trace_id(request: Request) -> Optional[str]:
    """Returns the active trace ID attached to request.state by the middleware."""
    return getattr(request.state, "trace_id", None)