from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from app.infrastructure.llm.vertex_adapter import VertexAdapter

router = APIRouter()
adapter = VertexAdapter()

class SimulationParams(BaseModel):
    ad_spend: float
    cpc: float
    conversion_rate: float
    aov: float
    unit_cost: float
    order_goal: float

@router.post("/run")
async def run_strategic_simulation(params: SimulationParams):
    """
    Runs a multidimensional business simulation based on marketing and operational parameters.
    """
    try:
        # 1. Business Logic
        projected_clicks = params.ad_spend / params.cpc if params.cpc > 0 else 0
        projected_conversions = projected_clicks * (params.conversion_rate / 100)
        
        # If no marketing spend, simulate based on hitting the goal volume
        sim_volume = projected_conversions if params.ad_spend > 0 else params.order_goal
        
        revenue = sim_volume * params.aov
        variable_costs = sim_volume * params.unit_cost
        total_costs = params.ad_spend + variable_costs
        
        profit = revenue - total_costs
        roi = (profit / total_costs * 100) if total_costs > 0 else 0
        roas = (revenue / params.ad_spend) if params.ad_spend > 0 else (revenue / (sim_volume * params.unit_cost) if sim_volume > 0 else 0) # Fallback to Margin-based ROAS or 0
        cac = (params.ad_spend / projected_conversions) if projected_conversions > 0 else 0
        
        goal_achievement = (projected_conversions / params.order_goal * 100) if params.order_goal > 0 else 100
        if params.ad_spend == 0:
            goal_achievement = 100 # In goal-only mode, we assume the goal is the target
        
        # 2. AI Narrative Generation
        prompt = f"""
        Analyze this business simulation for DeciFlow AI:
        AOV: ₹{params.aov:,.2f}
        Unit Cost: ₹{params.unit_cost:.2f}
        User's Order Goal: {params.order_goal:,.0f} units
        
        Projected Revenue: ₹{revenue:,.2f}
        Projected Conversions: {projected_conversions:,.0f}
        Projected Profit: ₹{profit:,.2f}
        ROI: {roi:.1f}%
        ROAS: {roas:.2f}x
        CAC: ₹{cac:.2f}
        Goal Achievement: {goal_achievement:.1f}%
        
        DO NOT use labels like "Executive Summary:", "Analysis:", or "Summary:". 
        DO NOT use introductory phrases. 
        Start immediately with the analysis. 
        Provide a concise, 2-sentence executive summary. Analyze if the projected conversions will hit the user's order goal. 
        Offer a "predictive insight" on whether the market can support this based on the ROAS/CAC efficiency.
        """
        
        narrative = await adapter.generate_content(prompt) or "Manual analysis required for this edge-case scenario."

        return {
            "status": "success",
            "data": {
                "projected_profit": round(profit, 2),
                "revenue": round(revenue, 2),
                "projected_conversions": round(sim_volume, 0),
                "roi": f"{round(roi, 1)}%",
                "roas": f"{round(roas, 2)}x" if params.ad_spend > 0 else "N/A",
                "cac": f"₹{round(cac, 2)}" if params.ad_spend > 0 else "₹0.00",
                "goal_achievement": f"{round(goal_achievement, 1)}%" if params.ad_spend > 0 else "Goal Scenario",
                "risk_level": "High" if roas < 2 or goal_achievement < 50 else "Medium" if roas < 4 else "Low",
                "narrative": narrative,
                "recommendation": "Scale Budget" if goal_achievement < 90 and roas > 4 else "Optimize Conversion" if roas < 3 else "Goal on Track"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
