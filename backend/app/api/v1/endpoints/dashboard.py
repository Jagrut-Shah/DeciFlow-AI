from fastapi import APIRouter
from app.schemas.response import APIResponse, success_response
import random

router = APIRouter()

@router.get("/insights", response_model=APIResponse)
async def get_dashboard_insights():
    """
    Returns dynamic AI insights for the dashboard.
    In a real app, this would fetch from the InsightService/Agent.
    """
    insights = [
        "We noticed a 15% surge in growth over the last 48 hours. Consider scaling up your ad spend.",
        "Operational efficiency is at an all-time high of 94.2%. Great job on the latest optimizations!",
        "Warning: Potential bottleneck detected in the supply chain simulation for next quarter.",
        "Revenue projections are trending up. The current price-to-demand ratio is optimal."
    ]
    
    return success_response(
        data={
            "main_insight": random.choice(insights),
            "stats": [
                {"label": "Revenue", "value": "$42,500", "trend": "+12.5%", "isPositive": True},
                {"label": "Growth", "value": "84.2%", "trend": "+5.2%", "isPositive": True},
                {"label": "Loss", "value": "$1,200", "trend": "-2.1%", "isPositive": False},
            ]
        },
        message="Dashboard insights retrieved successfully."
    )
