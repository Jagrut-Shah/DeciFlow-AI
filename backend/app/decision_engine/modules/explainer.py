from app.decision_engine.interfaces import IExplainer
from app.decision_engine.models import ScoredAction

class DefaultExplainer(IExplainer):
    def explain(self, top_action: ScoredAction) -> str:
        act = top_action.action
        return f"Action '{act.name}' was selected due to a robust score of {top_action.score:.2f} derived from {act.base_impact} impact and {act.base_confidence} confidence."
