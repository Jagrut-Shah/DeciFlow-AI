
"""
DeciFlow AI — InsightAgent
==========================
Stage 2 of the pipeline. Receives the structured output of DataAgent
and converts it into a concise list of human-readable business insights.

Each insight explains *what is currently happening* in the business —
no predictions, no recommendations.

Expected input (DataAgent output):
    {
        "processed_data":       [...],
        "metrics": {
            "total_sales":        float,
            "total_revenue":      float,
            "total_orders":       float,
            "average_sales":      float,
            "avg_order_value":    float | None,
            "trend":              str,
            "weekend_vs_weekday": { ... }
        },
        "category_performance": { "<category>": {"total_sales": float, "total_revenue": float} },
        "data_quality":         int,
        "issues":               [str, ...]
    }

Output shape:
    {
        "status":       "ok",
        "agent":        "InsightAgent",
        "main_insight": { ... },   # the single most important insight
        "insights": [
            {
                "text":       str,          # plain-English observation
                "priority":   "high" | "medium" | "low",
                "impact":     "positive" | "negative" | "neutral",
                "confidence": float         # 0.0 – 1.0
            },
            ...
        ]
    }
"""

from app.agents.base_agent import BaseAgent


# Data quality band thresholds (inclusive lower bound).
_QUALITY_HIGH   = 80
_QUALITY_MEDIUM = 50


class InsightAgent(BaseAgent):
    """
    Stage 2 agent — translates DataAgent output into business insights.

    Insight categories produced (where data permits):
    - Sales trend          (increasing / decreasing / stable)
    - Day-type performance (weekend vs. weekday)
    - Average order value  (AOV health)
    - Category performance (best and worst by revenue)
    - Data quality         (reliability signal)

    Rules:
    - One insight per observation — no duplication.
    - Plain language only; no jargon or numeric dumps.
    - Each insight is self-contained and actionable in meaning.
    """

    def __init__(self):
        super().__init__(name="InsightAgent")

    # ------------------------------------------------------------------
    # Core logic — called by BaseAgent.execute()
    # ------------------------------------------------------------------

    async def run(self, input_data: dict) -> dict:
        """
        Orchestrates insight generation from DataAgent output.
        """
        metrics              = input_data.get("metrics", {})
        category_performance = input_data.get("category_performance", {})
        data_quality         = input_data.get("data_quality", 100)

        insights: list[dict] = []

        insights += self._trend_insight(metrics)
        insights += self._day_type_insight(metrics.get("weekend_vs_weekday", {}))
        insights += self._aov_insight(metrics)
        insights += self._category_insight(category_performance)
        insights += self._quality_insight(data_quality)

        # Sort by importance: high priority first, negative impact first.
        _priority_rank = {"high": 3, "medium": 2, "low": 1}
        _impact_rank   = {"negative": 2, "positive": 1, "neutral": 0}
        insights.sort(
            key=lambda i: (
                _priority_rank.get(i["priority"], 0),
                _impact_rank.get(i["impact"], 0),
            ),
            reverse=True,
        )

        insights = insights[:6]

        # HYBRID LOGIC: Add AI Narrative and Structured Insights
        ai_narrative = "AI narrative generation skipped (Vertex AI not configured)."
        visualization = None
        try:
            from app.infrastructure.llm.vertex_adapter import VertexAdapter
            from app.core.config import settings
            
            is_fast_mode = input_data.get("mode") == "FAST"
            has_credentials = True
            if not is_fast_mode and has_credentials:
                adapter = VertexAdapter()
                
                # 1. Generate dynamic structured insights from LLM
                ai_insights = await adapter.generate_insights_structured(metrics, category_performance)
                
                # CRITICAL: If we have AI insights, we ONLY use them to ensure a high-fidelity experience.
                # If we don't have them, we keep the rule-based ones.
                if ai_insights and len(ai_insights) > 0:
                    for i in ai_insights:
                        i["confidence"] = round(i.get("confidence", 0.9), 2)
                    insights = ai_insights
                
                # 2. Generate strategic narrative
                ai_narrative = await adapter.generate_structured_insight({
                    "metrics": metrics,
                    "top_categories": list(category_performance.keys())[:3]
                }) or ai_narrative
                
                # 3. Generate dynamic visualization configuration
                visualization = await adapter.generate_visualization_config(metrics, category_performance)
        except Exception as e:
             self._log(f"AI Synthesis failed: {e}")

        # Final sort and trim
        insights.sort(
            key=lambda i: (
                _priority_rank.get(i.get("priority", "low"), 0),
                _impact_rank.get(i.get("impact", "neutral"), 0),
            ),
            reverse=True,
        )
        insights = insights[:10] # Allow slightly more insights if they are AI-generated

        return {
            "status":       "ok",
            "agent":        self.name,
            "main_insight": self._select_main_insight(insights),
            "insights":     insights,
            "all_insights": insights, # Add alias for easier mapping
            "ai_narrative": ai_narrative,
            "visualization": visualization
        }

    # ------------------------------------------------------------------
    # Insight generators
    # ------------------------------------------------------------------

    def _trend_insight(self, metrics: dict) -> list[dict]:
        """
        Generates one insight describing the overall sales trajectory.

        Uses metrics["trend"]:
            "increasing"       → positive growth signal
            "decreasing"       → decline warning
            "stable"           → steady performance
            "insufficient_data"→ not enough data to judge

        Args:
            metrics (dict): Full metrics block from DataAgent.

        Returns:
            list[dict]: Zero or one insight.
        """
        trend = metrics.get("trend")

        mapping = {
            "increasing": (
                "Sales are increasing.",
                "high", "positive", 0.85,
            ),
            "decreasing": (
                "Sales are declining.",
                "high", "negative", 0.85,
            ),
            "stable": (
                "Sales are stable with no major change.",
                "medium", "neutral", 0.80,
            ),
            "insufficient_data": (
                "Not enough data to determine a sales trend.",
                "low", "neutral", 0.40,
            ),
        }

        if trend not in mapping:
            return []

        text, priority, impact, confidence = mapping[trend]
        return [self._insight(text, priority, impact, confidence)]

    def _day_type_insight(self, wvw: dict) -> list[dict]:
        """
        Generates one insight comparing weekend vs. weekday sales performance.

        Skipped entirely when date information was unavailable (higher_performer
        is "unavailable" or the block is empty).

        Args:
            wvw (dict): The weekend_vs_weekday block from DataAgent metrics.

        Returns:
            list[dict]: Zero or one insight.
        """
        higher = wvw.get("higher_performer")

        if not higher or higher == "unavailable":
            return []

        if higher == "weekend":
            return [self._insight(
                "Weekend sales are higher than weekdays.",
                "medium", "positive", 0.80,
            )]

        if higher == "weekday":
            return [self._insight(
                "Weekday sales are higher than weekends.",
                "medium", "neutral", 0.80,
            )]

        # equal
        return [self._insight(
            "Weekend and weekday sales are evenly balanced.",
            "low", "neutral", 0.75,
        )]

    def _aov_insight(self, metrics: dict) -> list[dict]:
        """
        Generates one insight about the average order value (AOV).

        AOV is the ratio of total revenue to total orders. A None value
        means no orders were recorded, which is itself noteworthy.

        Args:
            metrics (dict): Full metrics block from DataAgent.

        Returns:
            list[dict]: Zero or one insight.
        """
        aov          = metrics.get("avg_order_value")
        total_orders = metrics.get("total_orders", 0)

        if aov is None:
            if total_orders == 0:
                return [self._insight(
                    "No orders were recorded in this dataset.",
                    "high", "negative", 0.95,
                )]
            return []

        avg_sales = metrics.get("average_sales", 0)

        if aov >= avg_sales and avg_sales > 0:
            return [self._insight(
                "Customers are spending well per order.",
                "medium", "positive", 0.75,
            )]

        return [self._insight(
            "Order values are lower than expected.",
            "medium", "negative", 0.70,
        )]

    def _category_insight(self, category_performance: dict) -> list[dict]:
        """
        Identifies the best and worst performing categories by total revenue
        and generates one insight for each.

        Skipped when fewer than two categories are present (no meaningful
        comparison can be made).

        Args:
            category_performance (dict): Category → {total_sales, total_revenue}.

        Returns:
            list[dict]: Zero, one, or two insights.
        """
        if len(category_performance) < 2:
            return []

        sorted_cats = sorted(
            category_performance.items(),
            key=lambda item: item[1].get("total_revenue", 0),
            reverse=True,
        )

        best_name,  best_data  = sorted_cats[0]
        worst_name, worst_data = sorted_cats[-1]

        insights = [
            self._insight(
                f"'{best_name}' is the best performing category.",
                "medium", "positive", 0.80,
            ),
            self._insight(
                f"'{worst_name}' is the lowest performing category.",
                "medium", "negative", 0.75,
            ),
        ]
        return insights

    def _quality_insight(self, data_quality: int) -> list[dict]:
        """
        Generates one insight describing the reliability of the underlying data.

        Bands:
            ≥ 80  → high quality   (positive signal)
            50–79 → moderate quality (caution)
            < 50  → low quality    (strong warning)

        Args:
            data_quality (int): 0–100 quality score from DataAgent.

        Returns:
            list[dict]: Exactly one insight.
        """
        if data_quality >= _QUALITY_HIGH:
            return [self._insight(
                "Data quality is high. Insights are reliable.",
                "low", "positive", 0.95,
            )]

        if data_quality >= _QUALITY_MEDIUM:
            return [self._insight(
                "Data quality is moderate. Some values were corrected.",
                "medium", "neutral", 0.65,
            )]

        return [self._insight(
            "Data quality is low. Insights may not be reliable.",
            "high", "negative", 0.40,
        )]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _select_main_insight(insights: list[dict]) -> dict | None:
        """
        Picks the single most important insight from the generated list.

        Selection priority (in order):
        1. High priority + negative impact  (critical warnings first)
        2. High priority + any impact
        3. Medium priority + negative impact
        4. First insight in the list        (fallback)

        The returned object is the same dict reference that already exists
        inside `insights` — it is not a copy or a new insight.

        Args:
            insights (list[dict]): All generated insights.

        Returns:
            dict | None: The main insight, or None if the list is empty.
        """
        if not insights:
            return None

        _priority_rank = {"high": 3, "medium": 2, "low": 1}
        _impact_rank   = {"negative": 2, "positive": 1, "neutral": 0}

        return max(
            insights,
            key=lambda i: (
                _priority_rank.get(i["priority"], 0),
                _impact_rank.get(i["impact"], 0),
            ),
        )

    @staticmethod
    def _insight(text: str, priority: str, impact: str, confidence: float) -> dict:
        """
        Constructs a single standardised insight object.

        Args:
            text       (str):   Plain-English observation.
            priority   (str):   "high" | "medium" | "low"
            impact     (str):   "positive" | "negative" | "neutral"
            confidence (float): 0.0 – 1.0; how certain the insight is.

        Returns:
            dict: Structured insight payload.
        """
        return {
            "text":       text,
            "priority":   priority,
            "impact":     impact,
            "confidence": round(confidence, 2),
        }