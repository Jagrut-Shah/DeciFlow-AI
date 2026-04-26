
"""
DeciFlow AI — PredictionAgent
==============================
Stage 3 of the pipeline. Receives output from DataAgent and InsightAgent
and generates simple, rule-based predictions about near-future business
performance.

Each prediction explains *what is likely to happen* based on current
signals — no recommendations, no actions.

Expected input:
    {
        "metrics": {
            "trend":              str,
            "weekend_vs_weekday": { "higher_performer": str, ... },
            ...
        },
        "category_performance": {
            "<category>": {"total_sales": float, "total_revenue": float}, ...
        },
        "insights": [ {"text": str, "priority": str, "impact": str, ...}, ... ]
    }

Output shape:
    {
        "status":      "ok",
        "agent":       "PredictionAgent",
        "predictions": [
            {
                "text":       str,    # what is expected to happen
                "reason":     str,    # why this prediction is made
                "confidence": float,  # 0.0 – 1.0
                "assumption": str     # condition under which this holds
            },
            ...
        ]
    }
"""

from app.agents.base_agent import BaseAgent


class PredictionAgent(BaseAgent):
    """
    Stage 3 agent — generates rule-based predictions from current business signals.

    Prediction categories produced (where data permits):
    - Sales trend      (continuing growth, decline, or stability)
    - Day-type         (weekend vs. weekday performance holding or shifting)
    - Category         (underperforming category likely to continue lagging)
    - Data quality     (low quality reduces prediction confidence signal)

    Rules:
    - One prediction per signal — no duplication.
    - Plain language only; no jargon or numeric dumps.
    - Every prediction carries a reason and a qualifying assumption.
    """

    def __init__(self):
        super().__init__(name="PredictionAgent")

    # ------------------------------------------------------------------
    # Core logic — called by BaseAgent.execute()
    # ------------------------------------------------------------------

    async def run(self, input_data: dict) -> dict:
        """
        Orchestrates prediction generation from upstream agent output.

        Args:
            input_data (dict): Combined output from DataAgent / InsightAgent.

        Returns:
            dict: {"status": "ok", "agent": ..., "predictions": [...]}
        """
        metrics              = input_data.get("metrics", {})
        category_performance = input_data.get("category_performance", {})
        data_quality         = input_data.get("data_quality", 100)

        predictions: list[dict] = []

        predictions += self._trend_prediction(metrics)
        predictions += self._day_type_prediction(metrics.get("weekend_vs_weekday", {}))
        predictions += self._category_prediction(category_performance)
        predictions += self._quality_prediction(data_quality)

        # HYBRID LOGIC: Add AI Predictions
        try:
            from app.infrastructure.llm.vertex_adapter import VertexAdapter
            from app.core.config import settings
            
            is_fast_mode = input_data.get("mode") == "FAST"
            has_credentials = settings.GOOGLE_APPLICATION_CREDENTIALS_PATH or settings.GOOGLE_API_KEY
            
            if not is_fast_mode and has_credentials:
                adapter = VertexAdapter()
                prompt = f"""
                Analyze these business metrics and provide 2-3 specific forecasts for the next period.
                Focus on potential risks or growth opportunities.
                
                METRICS: {metrics}
                
                RETURN JSON FORMAT ONLY:
                [
                  {{
                    "text": "What is likely to happen",
                    "reason": "Why this prediction is made",
                    "confidence": 0.0-1.0,
                    "assumption": "Condition under which this holds"
                  }}
                ]
                """
                response = await adapter.generate_content(prompt, model_type="flash")
                if response:
                    import json
                    import re
                    json_match = re.search(r'\[.*\]', response, re.DOTALL)
                    if json_match:
                        ai_preds = json.loads(json_match.group(0))
                        predictions = ai_preds + predictions
        except Exception as e:
            self._log(f"AI Predictions failed: {e}")

        # Signal-based confidence boost — no string matching.
        # A strong directional trend slightly increases trend prediction confidence.
        trend = metrics.get("trend")
        if predictions and trend in ("increasing", "decreasing"):
            predictions[0]["confidence"] = round(
                min(predictions[0]["confidence"] + 0.05, 1.0), 2
            )

        # Low data quality reduces confidence on the quality warning prediction only.
        if data_quality < 50 and predictions:
            predictions[-1]["confidence"] = round(
                max(predictions[-1]["confidence"] - 0.05, 0.0), 2
            )

        # Cap at 5 — keep the first (highest-signal) predictions.
        predictions = predictions[:5]

        return {
            "status":      "ok",
            "agent":       self.name,
            "predictions": predictions,
        }

    # ------------------------------------------------------------------
    # Prediction generators
    # ------------------------------------------------------------------

    def _trend_prediction(self, metrics: dict) -> list[dict]:
        """
        Generates one prediction based on the overall sales trend.

        Logic:
            "increasing"        → growth expected to continue
            "decreasing"        → decline expected to continue
            "stable"            → performance expected to hold
            "insufficient_data" → no reliable prediction possible

        Args:
            metrics (dict): Full metrics block from DataAgent.

        Returns:
            list[dict]: Zero or one prediction.
        """
        trend = metrics.get("trend")

        mapping = {
            "increasing": (
                "Sales are likely to continue growing.",
                "Sales have been trending upward consistently.",
                0.75,
                "If current market conditions remain unchanged.",
            ),
            "decreasing": (
                "Sales are likely to continue declining.",
                "Sales have been on a downward trend.",
                0.75,
                "If current trends persist.",
            ),
            "stable": (
                "Sales are likely to remain at current levels.",
                "Sales have shown no significant movement in either direction.",
                0.70,
                "If current conditions persist.",
            ),
            "insufficient_data": (
                "Sales trend cannot be predicted reliably.",
                "There is not enough data to identify a clear direction.",
                0.30,
                "If more data becomes available.",
            ),
        }

        if trend not in mapping:
            return []

        text, reason, confidence, assumption = mapping[trend]
        return [self._prediction(text, reason, confidence, assumption)]

    def _day_type_prediction(self, wvw: dict) -> list[dict]:
        """
        Generates one prediction about weekend vs. weekday performance.

        Skipped when date data was unavailable (higher_performer is
        "unavailable" or the block is empty).

        Args:
            wvw (dict): The weekend_vs_weekday block from DataAgent metrics.

        Returns:
            list[dict]: Zero or one prediction.
        """
        higher = wvw.get("higher_performer")

        if not higher or higher == "unavailable":
            return []

        if higher == "weekend":
            return [self._prediction(
                "Weekends are likely to remain the stronger sales period.",
                "Weekend sales have consistently outperformed weekdays.",
                0.70,
                "If customer behaviour patterns do not change.",
            )]

        if higher == "weekday":
            return [self._prediction(
                "Weekdays are likely to remain the stronger sales period.",
                "Weekday sales have consistently outperformed weekends.",
                0.70,
                "If customer behaviour patterns do not change.",
            )]

        # equal
        return [self._prediction(
            "Sales are likely to stay balanced across weekdays and weekends.",
            "No meaningful difference has been observed between weekday and weekend sales.",
            0.65,
            "If current demand patterns continue.",
        )]

    def _category_prediction(self, category_performance: dict) -> list[dict]:
        """
        Identifies the lowest-performing category by total revenue and
        predicts continued underperformance.

        Skipped when fewer than two categories are present (no meaningful
        comparison can be made).

        Args:
            category_performance (dict): Category → {total_sales, total_revenue}.

        Returns:
            list[dict]: Zero or one prediction.
        """
        if len(category_performance) < 2:
            return []

        worst_name = min(
            category_performance,
            key=lambda c: category_performance[c].get("total_revenue", 0),
        )

        return [self._prediction(
            f"'{worst_name}' may continue to underperform.",
            f"'{worst_name}' has the lowest revenue among all categories.",
            0.65,
            "If current conditions continue.",
        )]

    def _quality_prediction(self, data_quality: int) -> list[dict]:
        """
        Generates a prediction confidence warning when data quality is low.

        Only produces an insight when quality is below 50 — high and
        moderate quality do not require a dedicated prediction entry.

        Args:
            data_quality (int): 0–100 quality score from DataAgent.

        Returns:
            list[dict]: Zero or one prediction.
        """
        if data_quality < 50:
            return [self._prediction(
                "Predictions in this report may be unreliable.",
                "A significant portion of the input data had quality issues.",
                0.40,
                "Predictions assume the cleaned data is representative of actual performance.",
            )]

        return []

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    @staticmethod
    def _prediction(
        text: str, reason: str, confidence: float, assumption: str
    ) -> dict:
        """
        Constructs a single standardised prediction object.

        Args:
            text       (str):   Plain-English statement of what is expected.
            reason     (str):   Why this prediction is being made.
            confidence (float): 0.0 – 1.0; strength of the underlying signal.
            assumption (str):   Condition under which the prediction holds.

        Returns:
            dict: Structured prediction payload.
        """
        return {
            "text":       text,
            "reason":     reason,
            "confidence": round(confidence, 2),
            "assumption": assumption,
        }