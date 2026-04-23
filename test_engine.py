import sys
import os

# Ensure backend directory is in path for absolute imports
sys.path.append(os.path.abspath(r"c:\Users\HP\Downloads\DeciFlow AI\backend"))

from app.decision_engine.models import InsightInput, PredictionInput
from app.decision_engine.modules.generator import DefaultGenerator
from app.decision_engine.modules.scorer import DefaultScorer, ConservativeScorer
from app.decision_engine.modules.ranker import DefaultRanker
from app.decision_engine.modules.constraints import DefaultConstraintEngine
from app.decision_engine.modules.explainer import DefaultExplainer
from app.decision_engine.advanced.adaptive_learning import AdaptiveLearning
from app.decision_engine.advanced.feedback_loop import FeedbackLoop
from app.decision_engine.engine import DecisionIntelligenceEngine

import logging

logging.basicConfig(level=logging.INFO)

# Setup Dependencies
adaptive_learner = AdaptiveLearning()
feedback = FeedbackLoop(adaptive_learner)

# Instantiate Engine
engine = DecisionIntelligenceEngine(
    generator=DefaultGenerator(),
    scorer=ConservativeScorer(),
    ranker=DefaultRanker(),
    constraint_engine=DefaultConstraintEngine(),
    explainer=DefaultExplainer(),
    adaptive_learning=adaptive_learner
)

insight = InsightInput(
    insight_id="ins_777",
    context="High churn risk detected for segment A",
    metrics={"churn_probability": 0.85}
)

prediction = PredictionInput(
    prediction_id="pred_888",
    probabilities={"churn": 0.85, "retention": 0.15},
    confidence=0.92
)

# Run pipeline
result = engine.execute_pipeline(insight, prediction)
print("\n--- PIPELINE RESULT ---")
print(result.model_dump_json(indent=2))

# Simulate feedback loop adapting the scorer
print("\n--- INGESTING FEEDBACK (FAILURE) ---")
feedback.ingest_result("act_1", "FAILURE")
print(f"New Learning Weights: {adaptive_learner.get_weights()}")

# Run again to see scoring difference
result2 = engine.execute_pipeline(insight, prediction)
print("\n--- NEW PIPELINE RESULT ---")
print(result2.model_dump_json(indent=2))
