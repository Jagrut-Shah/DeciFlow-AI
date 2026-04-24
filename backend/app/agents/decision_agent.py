
"""
DeciFlow AI — DecisionAgent
============================
Stage 4 (final) of the pipeline. Receives insights and predictions from
upstream agents and produces 3–5 practical, traceable business decisions.

Each decision is rule-based, moderate in scope, and tied directly to the
insight or prediction that triggered it.

Expected input:
    {
        "insights": [
            {"text": str, "priority": str, "impact": str, "confidence": float},
            ...
        ],
        "main_insight": {"text": str, "priority": str, "impact": str, ...},
        "predictions":  [
            {"text": str, "reason": str, "confidence": float, "assumption": str},
            ...
        ]
    }

Output shape:
    {
        "status":    "ok",
        "agent":     "DecisionAgent",
        "decisions": [
            {
                "action":          str,    # what to do
                "type":            str,    # "pricing" | "discount" | "category" | "strategy"
                "priority":        str,    # "high" | "medium" | "low"
                "based_on":        str,    # insight text that triggered this decision
                "reason":          str,    # why this action is suggested
                "expected_impact": str,    # how it helps the business
                "confidence":      float   # 0.0 – 1.0
            },
            ...
        ]
    }
"""

import re
from base_agent import BaseAgent


# Decision count bounds.
_MIN_DECISIONS = 1
_MAX_DECISIONS = 5


class DecisionAgent(BaseAgent):
    """
    Stage 4 agent — converts insights and predictions into business decisions.

    Decision categories:
    - pricing   : adjusting price levels based on performance signals
    - discount  : applying or reducing discounts based on order/revenue signals
    - category  : acting on underperforming or overperforming product categories
    - strategy  : broader operational or focus adjustments

    Rules:
    - Each decision traces back to exactly one insight via "based_on".
    - Actions are gradual and moderate — no extreme changes.
    - If no major issue is found, a stable no-action decision is returned.
    - Final list is capped at _MAX_DECISIONS, ordered by priority.
    """

    def __init__(self):
        super().__init__(name="DecisionAgent")

    # ------------------------------------------------------------------
    # Core logic — called by BaseAgent.execute()
    # ------------------------------------------------------------------

    async def run(self, input_data: dict) -> dict:
        """
        Orchestrates decision generation from upstream agent output.
        """
        insights     = input_data.get("insights", [])
        main_insight = input_data.get("main_insight") or self._resolve_main_insight(insights)
        predictions  = input_data.get("predictions", [])

        decisions: list[dict] = []

        decisions += self._decisions_from_main_insight(main_insight)
        decisions += self._decisions_from_insights(insights, main_insight)
        decisions += self._decisions_from_predictions(predictions, insights)

        # One decision per type — keep the first (highest-signal) occurrence.
        decisions = self._deduplicate_by_type(decisions)

        # Sort: high → medium → low.
        _rank = {"high": 3, "medium": 2, "low": 1}
        decisions.sort(key=lambda d: _rank.get(d["priority"], 0), reverse=True)

        decisions = decisions[:_MAX_DECISIONS]

        if not decisions:
            decisions = [self._no_action_decision()]

        # HYBRID LOGIC: Add AI Strategic Advisory
        ai_advice = "AI advisory skipped (Vertex AI not configured)."
        try:
            from app.infrastructure.llm.vertex_adapter import VertexAdapter
            from app.core.config import settings
            
            if settings.GOOGLE_CLOUD_PROJECT != "your-project-id" and insights:
                adapter = VertexAdapter()
                ai_advice = await adapter.generate_strategic_advice(insights) or ai_advice
        except Exception as e:
             self._log(f"AI Strategic Advisory failed: {e}")

        return {
            "status":    "ok",
            "agent":     self.name,
            "decisions": decisions,
            "ai_strategic_advice": ai_advice
        }

    # ------------------------------------------------------------------
    # Decision generators
    # ------------------------------------------------------------------

    def _decisions_from_main_insight(self, main_insight: dict) -> list[dict]:
        """
        Derives the primary decision directly from main_insight.

        The main_insight is the single most important signal in the pipeline,
        so its decision receives the highest confidence and priority.

        Args:
            main_insight (dict): The main_insight block from InsightAgent.

        Returns:
            list[dict]: Zero or one decision.
        """
        if not main_insight:
            return []

        text   = main_insight.get("text", "")
        impact = main_insight.get("impact", "neutral")
        conf   = main_insight.get("confidence", 0.5)

        text_lower = text.lower()

        if "declining" in text_lower or "decreasing" in text_lower:
            return [self._decision(
                action          = "Review pricing to improve competitiveness.",
                dtype           = "pricing",
                priority        = "high",
                based_on        = text,
                reason          = "Sales are declining and pricing may be a contributing factor.",
                expected_impact = "Attract more buyers and slow the decline.",
                confidence      = round(min(conf + 0.05, 1.0), 2),
            )]

        if "increasing" in text_lower or "growing" in text_lower:
            return [self._decision(
                action          = "Maintain current pricing strategy.",
                dtype           = "pricing",
                priority        = "medium",
                based_on        = text,
                reason          = "Sales are growing under the current approach.",
                expected_impact = "Sustain momentum without disruption.",
                confidence      = round(min(conf + 0.05, 1.0), 2),
            )]

        if "low" in text_lower and "quality" in text_lower:
            return [self._decision(
                action          = "Improve data collection before acting on these insights.",
                dtype           = "strategy",
                priority        = "high",
                based_on        = text,
                reason          = "Low data quality reduces the reliability of all decisions.",
                expected_impact = "More accurate insights and safer decisions going forward.",
                confidence      = 0.80,
            )]

        if impact == "negative":
            return [self._decision(
                action          = "Monitor performance closely over the next period.",
                dtype           = "strategy",
                priority        = "high",
                based_on        = text,
                reason          = "A critical negative signal has been detected.",
                expected_impact = "Early visibility into worsening trends.",
                confidence      = round(conf, 2),
            )]

        return []

    def _decisions_from_insights(
        self, insights: list[dict], main_insight: dict
    ) -> list[dict]:
        """
        Scans supporting insights (excluding main_insight) for additional
        decision signals.

        Signals handled:
        - Weekend outperforms weekday → consider weekend-focused discounts.
        - Weekday outperforms weekend → concentrate efforts on weekday activity.
        - Data quality moderate/low   → flag reliability concern.

        Args:
            insights     (list): All insights from InsightAgent.
            main_insight (dict): Already handled above; skipped here.

        Returns:
            list[dict]: Zero or more decisions.
        """
        main_text  = main_insight.get("text", "")
        decisions  = []

        for insight in insights:
            text = insight.get("text", "")
            conf = insight.get("confidence", 0.5)

            # Skip the main insight — already processed.
            if text == main_text:
                continue

            text_lower = text.lower()

            if "weekend sales are higher" in text_lower:
                decisions.append(self._decision(
                    action          = "Offer targeted discounts on weekends to sustain the advantage.",
                    dtype           = "discount",
                    priority        = "medium",
                    based_on        = text,
                    reason          = "Weekends already show stronger demand.",
                    expected_impact = "Further boost weekend revenue.",
                    confidence      = round(conf, 2),
                ))

            elif "weekday sales are higher" in text_lower:
                decisions.append(self._decision(
                    action          = "Focus promotional activity on weekdays.",
                    dtype           = "strategy",
                    priority        = "medium",
                    based_on        = text,
                    reason          = "Weekday sales outperform weekends.",
                    expected_impact = "Strengthen the strongest sales period.",
                    confidence      = round(conf, 2),
                ))

            elif "moderate" in text_lower and "quality" in text_lower:
                decisions.append(self._decision(
                    action          = "Validate data sources before the next reporting cycle.",
                    dtype           = "strategy",
                    priority        = "low",
                    based_on        = text,
                    reason          = "Moderate data quality may affect decision accuracy.",
                    expected_impact = "Improve reliability of future insights.",
                    confidence      = round(conf, 2),
                ))

        return decisions

    def _decisions_from_predictions(
        self, predictions: list[dict], insights: list[dict]
    ) -> list[dict]:
        """
        Generates decisions from PredictionAgent output.

        Each prediction that carries a strong enough confidence signal
        produces at most one supporting decision.

        Signals handled:
        - Predicted continued decline      → discount to stimulate demand.
        - Predicted category underperformance → focus or rebalance category.

        Args:
            predictions (list): All predictions from PredictionAgent.
            insights    (list): Used only to find a matching based_on reference.

        Returns:
            list[dict]: Zero or more decisions.
        """
        decisions = []

        # Build a quick lookup: first insight text per impact for traceability.
        negative_insight = next(
            (i["text"] for i in insights if i.get("impact") == "negative"),
            "Prediction signal.",
        )

        for prediction in predictions:
            text = prediction.get("text", "")
            conf = prediction.get("confidence", 0.5)

            # Only act on reasonably confident predictions.
            if conf < 0.55:
                continue

            text_lower = text.lower()

            if "declining" in text_lower or "continue declining" in text_lower:
                decisions.append(self._decision(
                    action          = "Introduce limited-time discounts to stimulate demand.",
                    dtype           = "discount",
                    priority        = "high",
                    based_on        = negative_insight,
                    reason          = "A continued sales decline is predicted.",
                    expected_impact = "Short-term demand boost to slow the decline.",
                    confidence      = round(conf, 2),
                ))

            elif "underperform" in text_lower:
                # Extract category name between the first pair of quotes.
                category = self._extract_quoted(text) or "the underperforming category"
                decisions.append(self._decision(
                    action          = f"Review the product mix and visibility of {category}.",
                    dtype           = "category",
                    priority        = "medium",
                    based_on        = text,
                    reason          = f"{category.capitalize()} is predicted to keep underperforming.",
                    expected_impact = "Gradual improvement in category contribution.",
                    confidence      = round(conf, 2),
                ))

        return decisions

    # ------------------------------------------------------------------
    # No-action fallback
    # ------------------------------------------------------------------

    def _no_action_decision(self) -> dict:
        """
        Returns a stable no-action decision when no major signal is detected.

        Returns:
            dict: A single low-priority decision indicating stability.
        """
        return self._decision(
            action          = "No major action required.",
            dtype           = "strategy",
            priority        = "low",
            based_on        = "Overall business performance is stable.",
            reason          = "No significant negative signals were detected.",
            expected_impact = "Maintain current performance.",
            confidence      = 0.90,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_main_insight(insights: list[dict]) -> dict:
        """
        Selects the highest-priority insight as a fallback main_insight
        when none was provided by InsightAgent.

        Priority order: high > medium > low. Within the same priority,
        negative impact is preferred over positive, which beats neutral.

        Args:
            insights (list): All insights from InsightAgent.

        Returns:
            dict: The best available insight, or an empty dict if the
                  list is empty.
        """
        if not insights:
            return {}

        _priority_rank = {"high": 3, "medium": 2, "low": 1}
        _impact_rank   = {"negative": 2, "positive": 1, "neutral": 0}

        return max(
            insights,
            key=lambda i: (
                _priority_rank.get(i.get("priority", "low"), 0),
                _impact_rank.get(i.get("impact", "neutral"), 0),
            ),
        )

    @staticmethod
    def _conflicts_with(candidate: dict, existing: list[dict]) -> bool:
        """
        Returns True if the candidate decision contradicts an already-accepted
        decision, preventing conflicting actions from reaching the final list.

        Conflict rules:
        - A "pricing" decision to review / reduce price conflicts with a
          "discount" decision that also reduces cost to the buyer, when both
          target a declining signal (double-discount trap).
        - A "discount" decision conflicts with a "pricing" increase decision
          for the same situation.

        Detection is intentionally simple: it checks type pairs and scans
        action keywords rather than building a complex rule engine.

        Args:
            candidate (dict): The new decision being considered.
            existing  (list): Decisions already accepted.

        Returns:
            bool: True if a conflict is detected; False otherwise.
        """
        # Pairs of (type_a, type_b) that may conflict.
        _conflicting_pairs = {("pricing", "discount"), ("discount", "pricing")}

        candidate_type   = candidate.get("type", "")
        candidate_action = candidate.get("action", "").lower()

        for accepted in existing:
            accepted_type   = accepted.get("type", "")
            accepted_action = accepted.get("action", "").lower()

            pair = (candidate_type, accepted_type)
            if pair not in _conflicting_pairs:
                continue

            # Only a conflict when both actions are cost-reducing in nature.
            cost_reducing_keywords = ("discount", "reduc", "lower", "competi")
            candidate_is_reducing  = any(k in candidate_action for k in cost_reducing_keywords)
            accepted_is_reducing   = any(k in accepted_action  for k in cost_reducing_keywords)

            if candidate_is_reducing and accepted_is_reducing:
                return True

        return False

    def _deduplicate_by_type(self, decisions: list[dict]) -> list[dict]:
        """
        Keeps only the first decision for each type and rejects any decision
        that conflicts with one already accepted.

        Two guards applied per candidate:
        1. Type deduplication — one decision per type.
        2. Conflict check    — no contradicting actions (e.g. cut price + add
                               discount simultaneously for the same signal).

        Args:
            decisions (list): Raw decisions before deduplication.

        Returns:
            list[dict]: Deduplicated, conflict-free decisions.
        """
        seen    = set()
        deduped = []
        for d in decisions:
            if d["type"] in seen:
                continue
            if self._conflicts_with(d, deduped):
                continue
            seen.add(d["type"])
            deduped.append(d)
        return deduped

    @staticmethod
    def _extract_quoted(text: str) -> str:
        """
        Extracts the first single or double-quoted substring from a string.

        Used to pull category names out of prediction text like:
            "'Electronics' may continue to underperform."

        Args:
            text (str): Input string potentially containing 'quoted text' or "quoted text".

        Returns:
            str: The quoted content, or an empty string if not found.
        """
        # Supports both single and double quotes.
        # Captures everything inside the first pair of quotes.
        match = re.search(r"['\"](.*?)['\"]", text)
        return match.group(1) if match else ""

    @staticmethod
    def _decision(
        action: str,
        dtype: str,
        priority: str,
        based_on: str,
        reason: str,
        expected_impact: str,
        confidence: float,
    ) -> dict:
        """
        Constructs a single standardised decision object.

        Args:
            action          (str):   What the business should do.
            dtype           (str):   "pricing" | "discount" | "category" | "strategy"
            priority        (str):   "high" | "medium" | "low"
            based_on        (str):   The insight text that triggered this decision.
            reason          (str):   Why this action is suggested.
            expected_impact (str):   How it is expected to help.
            confidence      (float): 0.0 – 1.0.

        Returns:
            dict: Structured decision payload.
        """
        return {
            "action":          action,
            "type":            dtype,
            "priority":        priority,
            "based_on":        based_on,
            "reason":          reason,
            "expected_impact": expected_impact,
            "confidence":      round(confidence, 2),
        }