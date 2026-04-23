from typing import List
from app.decision_engine.interfaces import IConstraintEngine
from app.decision_engine.models import CandidateAction

class DefaultConstraintEngine(IConstraintEngine):
    def filter(self, actions: List[CandidateAction]) -> List[CandidateAction]:
        # Drop anything with terrible feasibility
        return [a for a in actions if a.base_feasibility > 0.2]
