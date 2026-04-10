from app.decision_engine.interfaces import IScorer
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
