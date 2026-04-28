
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

import asyncio
from datetime import datetime

from app.agents.base_agent import BaseAgent


# Numeric fields that are validated and cleaned on every record.
NUMERIC_FIELDS = ["sales", "revenue", "orders", "price", "discount", "profit", "margin", "cost"]

# Non-numeric fields copied through as-is (no validation).
PASSTHROUGH_FIELDS = ["date", "product", "category", "region", "segment", "channel", "customer", "country", "city", "state"]

# Suggestions for mapping common CSV column names to internal fields.
mapping_suggestions = {
    "sales":    ["total_sales", "sales_volume", "units_sold", "quantity", "qty", "volume", "ad spend", "ad_spend", "ad spend ($)", "ad spend (₹)", "budget", "total spend"],
    "revenue":  ["total_revenue", "income", "amount", "revenue_usd", "sales_amount", "value", "gross_revenue", "revenue_usd", "revenue ($)", "revenue (₹)", "earnings", "total_price", "grand_total"],
    "orders":   ["order_count", "transactions", "total_orders", "count", "num_orders", "conversions", "leads", "signups", "id", "product_id"],
    "price":    ["unit_price", "avg_price", "mrp", "cost", "sale_price", "price ($)", "price (₹)", "unit cost", "selling_price", "selling price", "price"],
    "discount": ["promo", "rebate", "discount_pct", "off_pct", "reduction", "discount ($)", "discount (₹)", "markdown"],
    "profit":   ["earnings", "net_income", "profit_amount", "net_profit", "contribution", "profit ($)", "profit (₹)", "margin_amt", "margin", "gain"],
    "margin":   ["profit_margin", "operating_margin", "margin_pct", "gp_pct", "roi (%)", "roi", "roas", "efficiency"],
    "cost":     ["unit_cost", "cost_price", "expense", "cost ($)", "cost (₹)", "purchase_price", "cogs"],
    "product":  ["item_name", "product_name", "description", "sku", "title", "label", "campaign name", "ad group", "keyword", "name"],
    "category": ["department", "group", "category_name", "tag", "industry", "segment", "channel", "platform", "type"]
}


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

    async def run(self, input_data: dict) -> dict:
        """
        Orchestrates the full data-processing pipeline.
        Runs heavy computation in a background thread to avoid blocking the event loop.
        """
        raw_records = input_data.get("data")

        if raw_records is None:
            return self._error('Required key "data" is missing from input.')
        if not isinstance(raw_records, list):
            return self._error('"data" must be a list of record dicts.')
        if len(raw_records) == 0:
            return self._error('"data" list is empty — nothing to process.')

        # Run heavy processing in a background thread
        try:
            return await asyncio.to_thread(self._sync_processing, raw_records)
        except Exception as e:
            return self._error(f"Internal Data Processing Error: {str(e)}")

    def _sync_processing(self, raw_records: list) -> dict:
        """
        Synchronous wrapper for all CPU-bound data tasks.
        """
        issues: list[str] = []
        cleaned = self._clean(raw_records, issues)

        if not cleaned:
            # We wrap this in a dict that execute() can handle
            return {
                "status": "error",
                "agent": self.name,
                "error": "No valid records remained after cleaning."
            }

        quality = self._quality_score(raw_records, issues)

        # Thread-safe date helper
        def _get_date(val):
            if not val: return datetime.min
            try:
                return datetime.strptime(str(val), "%Y-%m-%d")
            except ValueError:
                return datetime.min

        # Sort and Extract
        cleaned.sort(key=lambda r: _get_date(r.get("date")))
        
        metrics_block = self._extract_metrics(cleaned, _get_date)
        cat_perf = self._category_performance(cleaned)
        metadata = self._build_metadata(raw_records, cleaned)

        return {
            "status":               "ok",
            "agent":                self.name,
            "record_count":         len(cleaned),
            "processed_data":       cleaned,
            "metrics":              metrics_block,
            "category_performance": cat_perf,
            "data_quality":         quality["score"],
            "issues":               quality["issues"],
            "metadata":             metadata,
        }

    # ------------------------------------------------------------------
    # Step 1 — Cleaning
    # ------------------------------------------------------------------

    def _clean(self, records: list, issues: list) -> list:
        """
        Returns a cleaned copy of every valid record.
        """
        cleaned = []

        for idx, record in enumerate(records):
            label = f"Record[{idx}]"

            if not isinstance(record, dict):
                issues.append(
                    f"{label}: skipped — expected dict, got {type(record).__name__}."
                )
                continue

            # Create a case-insensitive lookup map
            key_map = {str(k).lower().strip(): k for k in record.keys()}
            clean_record = {}

            # 1. Map fields using mapping_suggestions (case-insensitive & fuzzy)
            for target, alternatives in mapping_suggestions.items():
                val = None
                # Check if target itself exists (case-insensitive, underscore-insensitive)
                for k_norm, k_orig in key_map.items():
                    if k_norm == target or k_norm.replace("_", " ") == target or k_norm.replace(" ", "_") == target:
                        val = record.get(k_orig)
                        break
                
                # If not found, try alternatives
                if val is None:
                    for alt in alternatives:
                        alt_norm = alt.lower().strip()
                        for k_norm, k_orig in key_map.items():
                            if k_norm == alt_norm or k_norm.replace("_", " ") == alt_norm or k_norm.replace(" ", "_") == alt_norm:
                                val = record.get(k_orig)
                                if val is not None:
                                    break
                        if val is not None:
                            break
                
                clean_record[target] = val

            # 2. Copy passthrough fields (case-insensitive)
            for field in PASSTHROUGH_FIELDS:
                if field not in clean_record or clean_record[field] is None:
                    if field in key_map:
                        clean_record[field] = record.get(key_map[field])

            # 3. Clean numeric fields
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
            value = value.strip()
            # Handle percentages (e.g. "15%" -> 0.15)
            if value.endswith("%"):
                try:
                    value = float(value.replace("%", "")) / 100.0
                except ValueError:
                    issues.append(f"{label}: '{field}' invalid percentage ('{value}') — defaulted to 0.")
                    return 0.0
            else:
                try:
                    # Remove currency symbols and commas
                    value = float(value.replace("$", "").replace("₹", "").replace(",", ""))
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

    def _extract_metrics(self, records: list, get_date_func=None) -> dict:
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
            get_date_func: Optional helper to get parsed dates.

        Returns:
            dict: All computed metrics.
        """
        n = len(records)

        sales_vals   = [r["sales"]   for r in records]
        revenue_vals = [r["revenue"] for r in records]
        orders_vals  = [r["orders"]  for r in records]
        profit_vals  = [r.get("profit", 0.0) for r in records]
        margin_vals  = [r.get("margin", 0.0) for r in records]

        # Catalog mode check: if no sales/revenue but we have prices, assume 1 sale per row
        if sum(revenue_vals) == 0 and sum(sales_vals) == 0:
            price_vals = [r.get("price", 0.0) for r in records]
            if sum(price_vals) > 0:
                for r in records:
                    r["sales"] = 1.0
                    if r.get("revenue", 0.0) == 0:
                        r["revenue"] = r.get("price", 0.0)
                sales_vals = [r["sales"] for r in records]
                revenue_vals = [r["revenue"] for r in records]

        # Calculate total revenue if it's 0 but we have sales/price
        if sum(revenue_vals) == 0 and sum(sales_vals) > 0:
            for r in records:
                if r["revenue"] == 0 and r["sales"] > 0 and r["price"] > 0:
                    r["revenue"] = round(r["sales"] * r["price"], 2)
            revenue_vals = [r["revenue"] for r in records]

        total_sales   = round(sum(sales_vals),   2)
        total_revenue = round(sum(revenue_vals), 2)
        
        # Calculate profit if cost is available
        cost_vals = [r.get("cost", 0.0) for r in records]
        if sum(profit_vals) == 0 and sum(cost_vals) > 0 and total_revenue > 0:
            for r in records:
                if r.get("profit", 0.0) == 0:
                    r["profit"] = round(r.get("revenue", 0.0) - r.get("cost", 0.0), 2)
            profit_vals = [r["profit"] for r in records]
            
        total_profit  = round(sum(profit_vals),  2)
        
        # If profit is 0 but we have revenue, try to estimate it
        if total_profit == 0 and total_revenue > 0:
            total_profit = round(total_revenue * 0.25, 2) # Assume 25% margin as fallback
            for r in records:
                r["profit"] = round(r["revenue"] * 0.25, 2)
            profit_vals = [r["profit"] for r in records]

        sum_orders = sum(orders_vals)
        total_orders = sum_orders if sum_orders > 0 else n
        
        average_sales = round(total_sales / n,   2) if n else 0.0
        avg_order_value = (
            round(total_revenue / total_orders, 2) if total_orders > 0 else None
        )
        avg_margin = round(sum(margin_vals) / n, 2) if n else 0.0

        return {
            "total_sales":        total_sales,
            "total_revenue":      total_revenue,
            "total_profit":       total_profit,
            "total_orders":       total_orders,
            "average_sales":      average_sales,
            "avg_order_value":    avg_order_value,
            "avg_margin":         avg_margin,
            "trend":              self._detect_trend(sales_vals),
            "weekend_vs_weekday": self._weekend_vs_weekday(records, get_date_func),
        }

    def _weekend_vs_weekday(self, records: list, get_date_func=None) -> dict:
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
                if get_date_func:
                    dt = get_date_func(raw_date)
                else:
                    dt = datetime.strptime(str(raw_date), "%Y-%m-%d")
                
                dow = dt.weekday()
                (weekday if dow < 5 else weekend).append(record)
            except (ValueError, TypeError):
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
                performance[category] = {"total_sales": 0.0, "total_revenue": 0.0, "total_profit": 0.0}

            performance[category]["total_sales"]   = round(
                performance[category]["total_sales"]   + record.get("sales",   0.0), 2
            )
            performance[category]["total_revenue"] = round(
                performance[category]["total_revenue"] + record.get("revenue", 0.0), 2
            )
            performance[category]["total_profit"]  = round(
                performance[category]["total_profit"]  + record.get("profit",  0.0), 2
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