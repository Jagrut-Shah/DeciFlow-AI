class AdaptiveLearning:
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
