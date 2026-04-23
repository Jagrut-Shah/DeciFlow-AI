from typing import List
from app.decision_engine.interfaces import IRanker
from app.decision_engine.models import ScoredAction

class DefaultRanker(IRanker):
    def rank(self, scored_actions: List[ScoredAction]) -> List[ScoredAction]:
        return sorted(scored_actions, key=lambda x: x.score, reverse=True)
