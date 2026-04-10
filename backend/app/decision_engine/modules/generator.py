from typing import List
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
