from pydantic import BaseModel, Field
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
