import os

base_dir = r"c:\Users\HP\Downloads\DeciFlow AI\backend\app\decision_engine"
os.makedirs(os.path.join(base_dir, "interfaces"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "modules"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "advanced"), exist_ok=True)

# --- MODELS ---
models_code = """from pydantic import BaseModel, Field
from typing import List, Optional

class InsightInput(BaseModel):
    insight_id: str
    context: str
    metrics: dict

class PredictionInput(BaseModel):
    prediction_id: str
    probabilities: dict
    confidence: float

class CandidateAction(BaseModel):
    action_id: str
    name: str
    base_impact: float
    base_confidence: float
    base_feasibility: float

class ScoredAction(BaseModel):
    action: CandidateAction
    score: float

class DecisionOutput(BaseModel):
    action: str
    impact: float
    confidence: float
    feasibility: float
    score: float
    explanation: str
"""
with open(os.path.join(base_dir, "models.py"), "w", encoding="utf-8") as f: f.write(models_code)
with open(os.path.join(base_dir, "__init__.py"), "w", encoding="utf-8") as f: f.write("")

# --- INTERFACES ---
interfaces_code = """from abc import ABC, abstractmethod
from typing import List
from app.decision_engine.models import InsightInput, PredictionInput, CandidateAction, ScoredAction, DecisionOutput

class IActionGenerator(ABC):
    @abstractmethod
    def generate(self, insight: InsightInput, prediction: PredictionInput) -> List[CandidateAction]: pass

class IScorer(ABC):
    @abstractmethod
    def score(self, action: CandidateAction, weights: dict) -> ScoredAction: pass

class IRanker(ABC):
    @abstractmethod
    def rank(self, scored_actions: List[ScoredAction]) -> List[ScoredAction]: pass

class IConstraintEngine(ABC):
    @abstractmethod
    def filter(self, actions: List[CandidateAction]) -> List[CandidateAction]: pass

class IExplainer(ABC):
    @abstractmethod
    def explain(self, top_action: ScoredAction) -> str: pass
"""
with open(os.path.join(base_dir, "interfaces", "__init__.py"), "w", encoding="utf-8") as f: f.write(interfaces_code)

# --- MODULES ---
gen_code = """from typing import List
from app.decision_engine.interfaces import IActionGenerator
from app.decision_engine.models import InsightInput, PredictionInput, CandidateAction

class DefaultGenerator(IActionGenerator):
    def generate(self, insight: InsightInput, prediction: PredictionInput) -> List[CandidateAction]:
        # Return fallback if context empty
        if not insight.context: return []
        return [
            CandidateAction(action_id="act_1", name="REDUCE_PRICE", base_impact=0.8, base_confidence=0.9, base_feasibility=0.7),
            CandidateAction(action_id="act_2", name="HOLD", base_impact=0.1, base_confidence=0.99, base_feasibility=0.99)
        ]
"""
with open(os.path.join(base_dir, "modules", "generator.py"), "w", encoding="utf-8") as f: f.write(gen_code)

scorer_code = """from app.decision_engine.interfaces import IScorer
from app.decision_engine.models import CandidateAction, ScoredAction

class DefaultScorer(IScorer):
    def score(self, action: CandidateAction, weights: dict = None) -> ScoredAction:
        w = weights or {"impact": 1.0, "confidence": 1.0, "feasibility": 1.0}
        score = (action.base_impact * w["impact"]) * (action.base_confidence * w["confidence"]) * (action.base_feasibility * w["feasibility"])
        return ScoredAction(action=action, score=score)

class ConservativeScorer(IScorer):
    def score(self, action: CandidateAction, weights: dict = None) -> ScoredAction:
        # Penalizes low confidence heavily
        w = weights or {"impact": 0.8, "confidence": 1.5, "feasibility": 1.0}
        penalty = 0.5 if action.base_confidence < 0.8 else 1.0
        score = (action.base_impact * w["impact"]) * (action.base_confidence * w["confidence"]) * (action.base_feasibility * w["feasibility"]) * penalty
        return ScoredAction(action=action, score=score)
"""
with open(os.path.join(base_dir, "modules", "scorer.py"), "w", encoding="utf-8") as f: f.write(scorer_code)

ranker_code = """from typing import List
from app.decision_engine.interfaces import IRanker
from app.decision_engine.models import ScoredAction

class DefaultRanker(IRanker):
    def rank(self, scored_actions: List[ScoredAction]) -> List[ScoredAction]:
        return sorted(scored_actions, key=lambda x: x.score, reverse=True)
"""
with open(os.path.join(base_dir, "modules", "ranker.py"), "w", encoding="utf-8") as f: f.write(ranker_code)

const_code = """from typing import List
from app.decision_engine.interfaces import IConstraintEngine
from app.decision_engine.models import CandidateAction

class DefaultConstraintEngine(IConstraintEngine):
    def filter(self, actions: List[CandidateAction]) -> List[CandidateAction]:
        # Drop anything with terrible feasibility
        return [a for a in actions if a.base_feasibility > 0.2]
"""
with open(os.path.join(base_dir, "modules", "constraints.py"), "w", encoding="utf-8") as f: f.write(const_code)

exp_code = """from app.decision_engine.interfaces import IExplainer
from app.decision_engine.models import ScoredAction

class DefaultExplainer(IExplainer):
    def explain(self, top_action: ScoredAction) -> str:
        act = top_action.action
        return f"Action '{act.name}' was selected due to a robust score of {top_action.score:.2f} derived from {act.base_impact} impact and {act.base_confidence} confidence."
"""
with open(os.path.join(base_dir, "modules", "explainer.py"), "w", encoding="utf-8") as f: f.write(exp_code)
with open(os.path.join(base_dir, "modules", "__init__.py"), "w", encoding="utf-8") as f: f.write("")

# --- ADVANCED ---
rl_code = """class AdaptiveLearning:
    def __init__(self):
        self.weights = {
            "impact": 1.0,
            "confidence": 1.0,
            "feasibility": 1.0
        }
        
    def get_weights(self) -> dict:
        return self.weights
        
    def adjust_weights(self, outcome: str):
        # Basic RL emulation
        if outcome == "FAILURE":
            # become more conservative
            self.weights["confidence"] += 0.1
            self.weights["feasibility"] += 0.1
        elif outcome == "SUCCESS":
            # favor impact slightly
            self.weights["impact"] += 0.05
"""
with open(os.path.join(base_dir, "advanced", "adaptive_learning.py"), "w", encoding="utf-8") as f: f.write(rl_code)

fb_code = """from app.decision_engine.advanced.adaptive_learning import AdaptiveLearning

class FeedbackLoop:
    def __init__(self, adaptive_learning: AdaptiveLearning):
        self.learner = adaptive_learning
        self.history = []
        
    def ingest_result(self, action_id: str, outcome: str):
        self.history.append({"action_id": action_id, "outcome": outcome})
        self.learner.adjust_weights(outcome)
"""
with open(os.path.join(base_dir, "advanced", "feedback_loop.py"), "w", encoding="utf-8") as f: f.write(fb_code)
with open(os.path.join(base_dir, "advanced", "__init__.py"), "w", encoding="utf-8") as f: f.write("")

# --- ENGINE ---
engine_code = """import time
import logging
from typing import Optional
import uuid

from app.decision_engine.interfaces import IActionGenerator, IScorer, IRanker, IConstraintEngine, IExplainer
from app.decision_engine.advanced.adaptive_learning import AdaptiveLearning
from app.decision_engine.models import InsightInput, PredictionInput, DecisionOutput

logger = logging.getLogger(__name__)

class DecisionIntelligenceEngine:
    def __init__(
        self,
        generator: IActionGenerator,
        scorer: IScorer,
        ranker: IRanker,
        constraint_engine: IConstraintEngine,
        explainer: IExplainer,
        adaptive_learning: Optional[AdaptiveLearning] = None
    ):
        self.generator = generator
        self.scorer = scorer
        self.ranker = ranker
        self.constraint_engine = constraint_engine
        self.explainer = explainer
        self.adaptive_learning = adaptive_learning

    def execute_pipeline(self, insight: InsightInput, prediction: PredictionInput) -> DecisionOutput:
        trace_id = str(uuid.uuid4())
        start_time = time.time()
        logger.info(f"[{trace_id}] Starting Decision Pipeline. Insight: {insight.insight_id}")
        
        try:
            # 1. Generate
            raw_actions = self.generator.generate(insight, prediction)
            logger.info(f"[{trace_id}] Generated {len(raw_actions)} raw actions.")
            if not raw_actions:
                return self._fallback("No raw actions generated.")
                
            # 2. Constraints
            valid_actions = self.constraint_engine.filter(raw_actions)
            logger.info(f"[{trace_id}] {len(valid_actions)} actions passed constraints.")
            if not valid_actions:
                return self._fallback("All actions constrained.")
                
            # 3. Score
            weights = self.adaptive_learning.get_weights() if self.adaptive_learning else None
            scored_actions = []
            for action in valid_actions:
                scored = self.scorer.score(action, weights)
                scored_actions.append(scored)
            logger.info(f"[{trace_id}] Scored {len(scored_actions)} actions safely.")
                
            # 4. Rank
            ranked = self.ranker.rank(scored_actions)
            top_action = ranked[0]
            
            # 5. Explain
            explanation = self.explainer.explain(top_action)
            
            exec_time = time.time() - start_time
            logger.info(f"[{trace_id}] Pipeline completed in {exec_time:.4f}s.")
            
            return DecisionOutput(
                action=top_action.action.name,
                impact=top_action.action.base_impact,
                confidence=top_action.action.base_confidence,
                feasibility=top_action.action.base_feasibility,
                score=top_action.score,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"[{trace_id}] Pipeline Failed: {str(e)}")
            return self._fallback(f"Pipeline error: {str(e)}")
            
    def _fallback(self, reason: str) -> DecisionOutput:
        return DecisionOutput(
            action="NO_ACTION",
            impact=0.0,
            confidence=0.0,
            feasibility=0.0,
            score=0.0,
            explanation=f"Fallback triggered. Reason: {reason}"
        )
"""
with open(os.path.join(base_dir, "engine.py"), "w", encoding="utf-8") as f: f.write(engine_code)

print("Decision Engine Scaffolding complete.")
