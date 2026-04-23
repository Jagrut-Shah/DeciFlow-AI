
"""
DeciFlow AI — DataAgent
=======================
Stage 1 of the pipeline. Ingests raw business records, cleans them,
extracts key metrics, scores data quality, and emits a normalised
payload ready for InsightAgent.

Supported fields per record:
    date       (str, YYYY-MM-DD)  — optional; enables time-based analysis
    sales      (numeric)          — optional
    revenue    (numeric)          — optional
    orders     (numeric)          — optional
    price      (numeric)          — optional; average price per unit
    discount   (numeric)          — optional; percentage discount
    product    (str)              — optional; passed through unchanged
    category   (str)              — optional; used for category aggregation

Output shape:
    {
        "status": "ok",
        "agent":  "DataAgent",
        "processed_data": [ ...cleaned records... ],
        "metrics": {
            "total_sales":      float,
            "total_revenue":    float,
            "total_orders":     float,
            "average_sales":    float,
            "avg_order_value":  float | None,
            "trend":            "increasing" | "decreasing" | "stable" | "insufficient_data",
            "weekend_vs_weekday": {
                "weekday_avg_sales":   float | None,
                "weekend_avg_sales":   float | None,
                "weekday_avg_revenue": float | None,
                "weekend_avg_revenue": float | None,
                "higher_performer":    "weekend" | "weekday" | "equal" | "unavailable"
            }
        },
        "category_performance": {
            "<category>": {"total_sales": float, "total_revenue": float}, ...
        },
        "data_quality": int,        # 0–100
        "issues":       [str, ...],
        "metadata": {
            "raw_record_count":       int,
            "processed_record_count": int,
            "fields_detected":        [str, ...],
            "processed_at":           "YYYY-MM-DD HH:MM:SS"
        }
    }
"""

from datetime import datetime

from base_agent import BaseAgent


# Numeric fields that are validated and cleaned on every record.
NUMERIC_FIELDS = ["sales", "revenue", "orders", "price", "discount"]

# Non-numeric fields copied through as-is (no validation).
PASSTHROUGH_FIELDS = ["date", "product", "category"]


class DataAgent(BaseAgent):
    """
    Stage 1 agent — cleans, enriches, and structures raw business records.

    Responsibilities:
    - Validate and clean numeric fields (nulls, negatives, bad types).
    - Extract aggregated business metrics (sales, revenue, orders, AOV).
    - Segment performance by weekday vs. weekend when dates are present.
    - Detect a simple sales trend (first-half vs. second-half comparison).
    - Score data quality and surface a list of field-level issues.
    - Attach a metadata block (counts, detected fields, timestamp).

    Inherits safe execution, input validation, logging, and error
    handling from BaseAgent. Only `run()` contains domain logic.
    """

    def __init__(self):
        super().__init__(name="DataAgent")

    # ------------------------------------------------------------------
    # Core logic — called by BaseAgent.execute()
    # ------------------------------------------------------------------

    def run(self, input_data: dict) -> dict:
        """
        Orchestrates the full data-processing pipeline.

        Args:
            input_data (dict): Must contain "data" — a list of record dicts.

        Returns:
            dict: Standardised output payload (see module docstring).
        """
        raw_records = input_data.get("data")

        if raw_records is None:
            return self._error('Required key "data" is missing from input.')
        if not isinstance(raw_records, list):
            return self._error('"data" must be a list of record dicts.')
        if len(raw_records) == 0:
            return self._error('"data" list is empty — nothing to process.')

        issues: list[str] = []
        cleaned = self._clean(raw_records, issues)

        if not cleaned:
            return self._error(
                "No valid records remained after cleaning. "
                "Check your data for missing or invalid values."
            )

        quality = self._quality_score(raw_records, issues)

        # Sort by date before extracting metrics to ensure trend detection is accurate.
        # Invalid dates are sorted to the beginning to minimize impact on the timeline.
        def _date_sort_key(r):
            raw_val = r.get("date")
            if not raw_val:
                return datetime.min
            try:
                return datetime.strptime(str(raw_val), "%Y-%m-%d")
            except ValueError:
                return datetime.min

        cleaned.sort(key=_date_sort_key)

        return {
            "status":               "ok",
            "agent":                self.name,
            "processed_data":       cleaned,
            "metrics":              self._extract_metrics(cleaned),
            "category_performance": self._category_performance(cleaned),
            "data_quality":         quality["score"],
            "issues":               quality["issues"],
            "metadata":             self._build_metadata(raw_records, cleaned),
        }

    # ------------------------------------------------------------------
    # Step 1 — Cleaning
    # ------------------------------------------------------------------

    def _clean(self, records: list, issues: list) -> list:
        """
        Returns a cleaned copy of every valid record.

        Per-record rules:
        - Non-dict records are skipped entirely (issue logged).
        - Each numeric field is sanitised via `_clean_numeric()`.
        - Passthrough and any extra fields are preserved unchanged.

        Args:
            records (list): Raw input records.
            issues  (list): Mutable; issues are appended in-place.

        Returns:
            list[dict]: Cleaned records only.
        """
        cleaned = []

        for idx, record in enumerate(records):
            label = f"Record[{idx}]"

            if not isinstance(record, dict):
                issues.append(
                    f"{label}: skipped — expected dict, got {type(record).__name__}."
                )
                continue

            clean_record = dict(record)  # shallow copy; preserves all original keys

            for field in NUMERIC_FIELDS:
                clean_record[field] = self._clean_numeric(
                    value=clean_record.get(field),
                    field=field,
                    label=label,
                    issues=issues,
                )

            cleaned.append(clean_record)

        return cleaned

    def _clean_numeric(self, value, field: str, label: str, issues: list) -> float:
        """
        Coerces a single field value to a valid non-negative float.

        Rules (in order):
        1. None / missing  → 0.0  (issue logged)
        2. String          → attempt float conversion; 0.0 on failure
        3. Non-numeric type → 0.0  (issue logged)
        4. Negative number → 0.0  (issue logged)

        Args:
            value  : Raw value from the record.
            field  : Field name, used in issue messages.
            label  : Record identifier, e.g. "Record[2]".
            issues : Mutable issues list; appended to on problems.

        Returns:
            float: Sanitised value, always ≥ 0.0.
        """
        if value is None:
            issues.append(f"{label}: '{field}' is missing — defaulted to 0.")
            return 0.0

        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                issues.append(
                    f"{label}: '{field}' could not be parsed ('{value}') — defaulted to 0."
                )
                return 0.0

        if not isinstance(value, (int, float)):
            issues.append(
                f"{label}: '{field}' has unexpected type {type(value).__name__} — defaulted to 0."
            )
            return 0.0

        if value < 0:
            issues.append(
                f"{label}: '{field}' is negative ({value}) — defaulted to 0."
            )
            return 0.0

        return float(value)

    # ------------------------------------------------------------------
    # Step 2 — Metric extraction
    # ------------------------------------------------------------------

    def _extract_metrics(self, records: list) -> dict:
        """
        Computes all business metrics from cleaned records.

        Metrics produced:
        - total_sales, total_revenue, total_orders
        - average_sales
        - avg_order_value  (total_revenue ÷ total_orders; None when orders = 0)
        - trend            (sales trajectory — see `_detect_trend`)
        - weekend_vs_weekday (segmented averages — see `_weekend_vs_weekday`)

        Args:
            records (list): Cleaned records from `_clean()`.

        Returns:
            dict: All computed metrics.
        """
        n = len(records)

        sales_vals   = [r["sales"]   for r in records]
        revenue_vals = [r["revenue"] for r in records]
        orders_vals  = [r["orders"]  for r in records]

        total_sales   = round(sum(sales_vals),   2)
        total_revenue = round(sum(revenue_vals), 2)
        total_orders  = round(sum(orders_vals),  2)
        average_sales = round(total_sales / n,   2) if n else 0.0
        avg_order_value = (
            round(total_revenue / total_orders, 2) if total_orders > 0 else None
        )

        return {
            "total_sales":        total_sales,
            "total_revenue":      total_revenue,
            "total_orders":       total_orders,
            "average_sales":      average_sales,
            "avg_order_value":    avg_order_value,
            "trend":              self._detect_trend(sales_vals),
            "weekend_vs_weekday": self._weekend_vs_weekday(records),
        }

    def _weekend_vs_weekday(self, records: list) -> dict:
        """
        Segments records by day type using the "date" field (YYYY-MM-DD)
        and computes average sales and revenue for weekdays and weekends.

        Records with an absent or unparseable date are silently excluded
        from this calculation only — they remain in processed_data.

        Returns:
            dict:
                weekday_avg_sales   (float | None)
                weekend_avg_sales   (float | None)
                weekday_avg_revenue (float | None)
                weekend_avg_revenue (float | None)
                higher_performer    ("weekend" | "weekday" | "equal" | "unavailable")
        """
        weekday: list[dict] = []
        weekend: list[dict] = []

        for record in records:
            raw_date = record.get("date")
            if not raw_date:
                continue
            try:
                dow = datetime.strptime(str(raw_date), "%Y-%m-%d").weekday()
                (weekday if dow < 5 else weekend).append(record)
            except ValueError:
                continue

        def _avg(bucket: list[dict], field: str) -> float | None:
            vals = [r[field] for r in bucket]
            return round(sum(vals) / len(vals), 2) if vals else None

        wd_sales = _avg(weekday, "sales")
        we_sales = _avg(weekend, "sales")

        if wd_sales is None or we_sales is None:
            higher = "unavailable"
        elif we_sales > wd_sales:
            higher = "weekend"
        elif wd_sales > we_sales:
            higher = "weekday"
        else:
            higher = "equal"

        return {
            "weekday_avg_sales":   wd_sales,
            "weekend_avg_sales":   we_sales,
            "weekday_avg_revenue": _avg(weekday, "revenue"),
            "weekend_avg_revenue": _avg(weekend, "revenue"),
            "higher_performer":    higher,
        }

    def _detect_trend(self, sales_values: list) -> str:
        """
        Infers a simple trend by comparing the first-half average of
        time-ordered sales values against the second-half average.

        A ±5 % threshold separates "stable" from directional trends.
        Requires at least 4 records; returns "insufficient_data" otherwise.

        Returns:
            "increasing" | "decreasing" | "stable" | "insufficient_data"
        """
        if len(sales_values) < 4:
            return "insufficient_data"

        mid        = len(sales_values) // 2
        first_avg  = sum(sales_values[:mid]) / mid
        second_avg = sum(sales_values[mid:]) / (len(sales_values) - mid)

        if first_avg == 0:
            return "insufficient_data"

        change_pct = (second_avg - first_avg) / first_avg * 100

        if change_pct > 5:
            return "increasing"
        if change_pct < -5:
            return "decreasing"
        return "stable"

    # ------------------------------------------------------------------
    # Step 3 — Category aggregation
    # ------------------------------------------------------------------

    def _category_performance(self, records: list) -> dict:
        """
        Groups cleaned records by their "category" field and aggregates
        total sales and total revenue per group.

        Records without a category (missing or empty) are grouped under
        the key "uncategorised" so they are never silently dropped.

        Args:
            records (list): Cleaned records from `_clean()`.

        Returns:
            dict: Mapping of category name → {"total_sales": float, "total_revenue": float}.

        Example output:
            {
                "Electronics": {"total_sales": 1200.0, "total_revenue": 36000.0},
                "Clothing":    {"total_sales":  800.0, "total_revenue": 12000.0}
            }
        """
        performance: dict[str, dict] = {}

        for record in records:
            category = str(record.get("category") or "Uncategorised").strip().title() or "Uncategorised"

            if category not in performance:
                performance[category] = {"total_sales": 0.0, "total_revenue": 0.0}

            performance[category]["total_sales"]   = round(
                performance[category]["total_sales"]   + record.get("sales",   0.0), 2
            )
            performance[category]["total_revenue"] = round(
                performance[category]["total_revenue"] + record.get("revenue", 0.0), 2
            )

        return performance

    # ------------------------------------------------------------------
    # Step 4 — Data quality
    # ------------------------------------------------------------------

    def _quality_score(self, raw_records: list, issues: list) -> dict:
        """
        Produces a 0–100 quality score based on field-level issue rate.

            score = 100 × (1 − issue_count / total_checks)

        where total_checks = len(raw_records) × len(NUMERIC_FIELDS).

        Args:
            raw_records (list): Original, unmodified records.
            issues      (list): Issues collected during `_clean()`.

        Returns:
            dict: {"score": int, "issues": [str, ...]}
        """
        total_checks = len(raw_records) * len(NUMERIC_FIELDS)
        score = (
            max(0, round((1 - len(issues) / total_checks) * 100))
            if total_checks else 0
        )
        return {"score": score, "issues": issues}

    # ------------------------------------------------------------------
    # Step 5 — Metadata
    # ------------------------------------------------------------------

    def _build_metadata(self, raw_records: list, cleaned_records: list) -> dict:
        """
        Builds a lightweight metadata block for observability.

        Args:
            raw_records     (list): Records before cleaning.
            cleaned_records (list): Records after cleaning.

        Returns:
            dict: Record counts, detected field names, and a timestamp.
        """
        detected_fields = sorted({
            key
            for record in cleaned_records
            if isinstance(record, dict)
            for key in record
        })

        return {
            "raw_record_count":       len(raw_records),
            "processed_record_count": len(cleaned_records),
            "fields_detected":        detected_fields,
            "processed_at":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }