from app.decision_engine.advanced.adaptive_learning import AdaptiveLearning

class FeedbackLoop:
    def __init__(self, adaptive_learning: AdaptiveLearning):
        self.learner = adaptive_learning
        self.history = []
        
    def ingest_result(self, action_id: str, outcome: str):
        self.history.append({"action_id": action_id, "outcome": outcome})
        self.learner.adjust_weights(outcome)
