from abc import ABC, abstractmethod
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
