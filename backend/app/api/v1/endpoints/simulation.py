from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from app.infrastructure.llm.vertex_adapter import VertexAdapter

router = APIRouter()
adapter = VertexAdapter()

class SimulationParams(BaseModel):
    price: float
    demand: float
    mode: str = "aggressive"

@router.post("/run")
async def run_strategic_simulation(params: SimulationParams):
    """
    Runs a strategic simulation based on price and demand parameters.
    """
    try:
        # 1. Economic Logic
        cost_per_unit = 25.0
        revenue = params.price * params.demand
        total_cost = cost_per_unit * params.demand
        profit = revenue - total_cost
        roi = (profit / total_cost * 100) if total_cost > 0 else 0
        
        # 2. AI Narrative Generation
        prompt = f"""
        Analyze this business scenario for DeciFlow AI:
        Price: ${params.price}
        Expected Demand: {params.demand} units
        Projected Profit: ${profit:,.2f}
        ROI: {roi:.1f}%
        
        Provide a concise, 2-sentence executive summary of this move's strategic value and the primary risk. 
        Keep it professional and data-driven.
        """
        
        narrative = await adapter.generate_content(prompt) or "Manual analysis required for this edge-case scenario."

        return {
            "status": "success",
            "data": {
                "projected_profit": round(profit, 2),
                "revenue": round(revenue, 2),
                "roi": f"{round(roi, 1)}%",
                "risk_level": "High" if params.price > 100 else "Medium",
                "narrative": narrative,
                "recommendation": "Generate PDF Report" if profit > 50000 else "Adjust Parameters"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
