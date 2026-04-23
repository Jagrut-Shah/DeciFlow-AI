import time
import logging
from typing import Optional
import uuid

from app.decision_engine.interfaces import IActionGenerator, IScorer, IRanker, IConstraintEngine, IExplainer
from app.decision_engine.advanced.adaptive_learning import AdaptiveLearning
from app.decision_engine.models import InsightInput, PredictionInput, DecisionOutput

logger = logging.getLogger(__name__)

class DecisionIntelligenceEngine:
    def __init__(
        self,
        generator: IActionGenerator,
        scorer: IScorer,
        ranker: IRanker,
        constraint_engine: IConstraintEngine,
        explainer: IExplainer,
        adaptive_learning: Optional[AdaptiveLearning] = None
    ):
        self.generator = generator
        self.scorer = scorer
        self.ranker = ranker
        self.constraint_engine = constraint_engine
        self.explainer = explainer
        self.adaptive_learning = adaptive_learning

    def execute_pipeline(
        self,
        insight: InsightInput,
        prediction: PredictionInput,
        trace_id: Optional[str] = None,
    ) -> DecisionOutput:
        trace_id = trace_id or str(uuid.uuid4())  # reuse caller's trace; generate only if absent
        start_time = time.time()
        logger.info(
            "Decision pipeline starting",
            extra={"trace_id": trace_id, "insight_id": insight.insight_id},
        )
        
        try:
            # 1. Generate
            raw_actions = self.generator.generate(insight, prediction)
            logger.info(f"Generated {len(raw_actions)} raw actions", extra={"trace_id": trace_id})
            if not raw_actions:
                return self._fallback("No raw actions generated.", trace_id)
                
            # 2. Constraints
            valid_actions = self.constraint_engine.filter(raw_actions)
            logger.info(f"{len(valid_actions)} actions passed constraints", extra={"trace_id": trace_id})
            if not valid_actions:
                return self._fallback("All actions constrained.", trace_id)
                
            # 3. Score
            weights = self.adaptive_learning.get_weights() if self.adaptive_learning else None
            scored_actions = [self.scorer.score(action, weights) for action in valid_actions]
            logger.info(f"Scored {len(scored_actions)} actions", extra={"trace_id": trace_id})
                
            # 4. Rank
            ranked = self.ranker.rank(scored_actions)
            top_action = ranked[0]
            
            # 5. Explain
            explanation = self.explainer.explain(top_action)
            
            exec_time = time.time() - start_time
            logger.info(
                "Decision pipeline completed",
                extra={"trace_id": trace_id, "action": top_action.action.name,
                       "score": top_action.score, "elapsed_ms": round(exec_time * 1000, 2)},
            )
            
            return DecisionOutput(
                action=top_action.action.name,
                impact=top_action.action.base_impact,
                confidence=top_action.action.base_confidence,
                feasibility=top_action.action.base_feasibility,
                score=top_action.score,
                explanation=explanation,
            )

        except (ValueError, KeyError, AttributeError, TypeError) as e:
            # Operational failures — safe to absorb and return fallback
            logger.error(
                "Decision pipeline operational error",
                exc_info=True,
                extra={"trace_id": trace_id, "error": str(e)},
            )
            return self._fallback(f"Operational error: {e}", trace_id)
        # Note: RuntimeError, AssertionError, etc. are NOT caught — they propagate
        # as they indicate programming bugs that should surface immediately.
            
    def _fallback(self, reason: str, trace_id: Optional[str] = None) -> DecisionOutput:
        logger.warning(
            "Decision fallback triggered",
            extra={"trace_id": trace_id, "reason": reason},
        )
        return DecisionOutput(
            action="NO_ACTION",
            impact=0.0,
            confidence=0.0,
            feasibility=0.0,
            score=0.0,
            explanation=f"Fallback triggered. Reason: {reason}",
        )

