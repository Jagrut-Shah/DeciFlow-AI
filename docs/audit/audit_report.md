# Technical Audit: DeciFlow AI Agents

This audit evaluates the core logic of the agents in `backend/app/agents/`. Since LLM integration is planned as a separate layer by the Backend Lead, this review focuses on **data integrity, logic robustness, and mathematical correctness.**

---

### 1. Faulty Trend Detection Logic
**Location**: `DataAgent._detect_trend` (Lines 318–346)

*   **Mistake**: The logic compares the first half of the data list to the second half without sorting by date.
*   **Reason**: It assumes the input `sales_values` is already time-ordered. If the user uploads a CSV where rows are out of order (very common), the "Trend" will be mathematically random and incorrect.
*   **Recommendation**: The `DataAgent` should explicitly sort the `processed_data` list by the `date` field before calculating trends.

### 2. Case-Sensitive Analytics Fragmentation
**Location**: `DataAgent._category_performance` (Lines 351–386)

*   **Mistake**: Category names are used as keys directly: `record.get("category")`.
*   **Reason**: "Electronics" and "electronics" will be treated as two different categories. In my tests, this resulted in one being the "Best Performer" and the other being the "Worst Performer" for the same product group.
*   **Recommendation**: Use `.strip().lower()` (or `.title()`) when creating category keys to ensure data is normalized.

### 3. Incomplete Metadata Validation in Quality Score
**Location**: `DataAgent._quality_score` (Lines 392–412)

*   **Mistake**: The `total_checks` only counts `NUMERIC_FIELDS`.
*   **Reason**: If the `date` field is missing or the `category` is null, the "Data Quality Score" remains 100% because those fields aren't tracked in the penalty logic. This gives the user a false sense of security about their data.
*   **Recommendation**: Include critical metadata fields (`date`, `category`) in the `total_checks` calculation.

### 4. Fragile String Extraction
**Location**: `DecisionAgent._extract_quoted` (Lines 453–472)

*   **Mistake**: The function only returns the **first** quoted substring it finds.
*   **Reason**: If a prediction or insight mentions two categories (e.g., "'Electronics' is up but 'Clothing' is down"), the decision logic will only see the first one. It also fails if the teammate uses double quotes (`"`) instead of single quotes (`'`).
*   **Recommendation**: Use regex (`re.findall`) to capture all quoted items or support both quote types.

### 5. Information Siloing in Sorting
**Location**: `InsightAgent.run` (Lines 111–112)

*   **Mistake**: Hard-capping at 6 insights **after** sorting.
*   **Reason**: If there are 10 "High Priority" issues, 4 of them will be silently deleted from the report. If the sorting logic has any bias, high-impact "Negative" insights could be pushed out by "Positive" ones of the same priority.
*   **Recommendation**: Instead of a hard cap, use a "Main Insight" + "Supporting Insights" model, or allow the UI to handle the display limit so no data is lost at the agent level.

---

### Summary of Testing
I ran a custom test suite (`scratch/agent_test_runner.py`) representing three scenarios:
1.  **Healthy Growth**: Passed (Logic held because data was pre-sorted).
2.  **Declining & Case Sensitive**: **FAILED**. Data results were split between "Electronics" and "electronics".
3.  **Low Data Quality**: **PARTIAL PASS**. Detected bad numbers, but didn't penalize for missing dates.

> [!TIP]
> Fixing these core logic issues will provide a "Solid Foundation" for your upcoming LLM integration. Without these fixes, the LLM will be reasoning on top of fragmented and potentially out-of-order data.
