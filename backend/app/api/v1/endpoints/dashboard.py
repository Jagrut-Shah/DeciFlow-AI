from fastapi import APIRouter, Depends
from app.schemas.response import APIResponse, success_response
from app.core.dependencies import get_result_store
from app.core.result_store import ResultStore

router = APIRouter()

@router.get("/insights", response_model=APIResponse)
async def get_dashboard_insights(store: ResultStore = Depends(get_result_store)):
    """
    Returns dynamic AI insights for the dashboard from the most recent pipeline run.
    """
    state = await store.get_latest_result() if store else None

    if not state:
        return success_response(
            data={
                "main_insight": "Awaiting multi-agent synthesis. Please upload a dataset.",
                "stats": [],
                "chart_data": [0, 0, 0, 0, 0],
                "all_insights": []
            },
            message="No pipeline data available."
        )

    # ── Extract data from each pipeline stage ──────────────────────────────
    data_output = state.raw_data if isinstance(state.raw_data, dict) else {}
    insight_output = state.insights if isinstance(state.insights, dict) else {}
    decision_output = state.decisions if isinstance(state.decisions, dict) else {}
    simulation_output = state.simulation if isinstance(state.simulation, dict) else {}

    # ── Extract primary metrics with fallbacks ─────────────────────────────
    # Check both flat and nested (from DataAgent) structures
    metrics = data_output.get("metrics", {})
    record_count = metrics.get("record_count") or data_output.get("record_count", 0)
    total_sales = metrics.get("total_sales", 0)
    total_profit = metrics.get("total_profit", 0)
    avg_margin = metrics.get("avg_margin", 0)
    
    fields_detected = data_output.get("metadata", {}).get("fields_detected", [])
    
    anomaly = insight_output.get("anomaly_detected", False)
    
    projected_roi = simulation_output.get("projected_roi", 1.0)
    risk_level = simulation_output.get("risk_level", "low")
    
    decision_action = decision_output.get("action", "MONITOR_TRENDS")
    decision_score = decision_output.get("score", 0.0)

    # ── Main insight text (Prioritize AI Narrative) ────────────────────────
    all_insights = insight_output.get("all_insights", [])
    ai_narrative = insight_output.get("ai_narrative")
    ai_advice = decision_output.get("ai_strategic_advice")
    
    main_insight = ai_narrative or insight_output.get("context") or insight_output.get("insights_summary")
    
    if not main_insight or main_insight == "Analysis complete.":
        if all_insights and len(all_insights) > 0:
            first = all_insights[0]
            main_insight = first.get("text") or main_insight
            
    if not main_insight:
        main_insight = "Analysis complete. Review metrics below."

    # ── Extract chart data (dynamic trend from processed data) ────────────
    chart_data = []
    processed_rows = data_output.get("processed_data", [])
    
    if processed_rows and isinstance(processed_rows, list):
        # Find best numeric field to plot (priority order)
        first_row = processed_rows[0]
        numeric_field = None
        priority_fields = ["sales", "revenue", "profit", "orders", "income", "loan_amount", "price"]
        for pf in priority_fields:
            if pf in first_row:
                numeric_field = pf
                break
        
        if not numeric_field:
            for k, v in first_row.items():
                try:
                    float(str(v).replace('$', '').replace('₹', '').replace(',', ''))
                    numeric_field = k
                    break
                except (ValueError, TypeError):
                    continue
        
        if numeric_field:
            # Sample max 50 points spread across the entire dataset for a meaningful trend
            total_rows = len(processed_rows)
            stride = max(1, total_rows // 50)
            sampled_rows = processed_rows[::stride]
            
            for row in sampled_rows:
                try:
                    val = float(str(row.get(numeric_field, 0)).replace('$', '').replace('₹', '').replace(',', ''))
                    chart_data.append(val)
                except (ValueError, TypeError):
                    continue
    
    if not chart_data:
        chart_data = [0, 0, 0, 0, 0]

    # ── Map risk to a cleaner label ────────────────────────────────────
    if anomaly and risk_level == "high":
        risk_label = "CRITICAL"
        risk_is_positive = False
    elif anomaly or risk_level == "high":
        risk_label = "ELEVATED"
        risk_is_positive = False
    elif risk_level == "medium":
        risk_label = "MODERATE"
        risk_is_positive = True
    else:
        risk_label = "OPTIMIZED"
        risk_is_positive = True

    stats = [
        {
            "label": "Projected ROI",
            "value": f"{projected_roi:.2f}x",
            "trend": "Growth Projection",
            "isPositive": projected_roi > 1.2
        },
        {
            "label": "Strategic Risk",
            "value": risk_label,
            "trend": "Security Audit" if anomaly else "Normal Ops",
            "isPositive": risk_is_positive
        }
    ]

    # Add Profit if available
    if total_profit > 0:
        stats.append({
            "label": "Total Profit",
            "value": f"₹{total_profit:,.2f}",
            "trend": f"{avg_margin*100:.1f}% Avg Margin",
            "isPositive": total_profit > 0
        })
    else:
        # Fallback to Data Volume
        stats.append({
            "label": "Data Volume",
            "value": f"{record_count:,}",
            "trend": f"{len(fields_detected)} Dimensions",
            "isPositive": record_count > 0
        })

    stats.append({
        "label": "Primary Strategy",
        "value": decision_action.replace("_", " ").title(),
        "trend": f"Impact: {decision_score * 100:.0f}%",
        "isPositive": decision_score > 0.4
    })

    return success_response(
        data={
            "main_insight": main_insight,
            "ai_strategic_advice": ai_advice,
            "stats": stats,
            "visualization": insight_output.get("visualization"),
            "chart_data": chart_data,
            "all_insights": insight_output.get("all_insights") or insight_output.get("insights") or [],
            "all_decisions": decision_output.get("all_decisions") or decision_output.get("decisions") or []
        },
        message="Dashboard insights retrieved successfully."
    )
