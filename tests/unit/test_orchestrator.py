import sys
import os
import asyncio

sys.path.append(os.path.abspath(r"c:\Users\HP\Downloads\DeciFlow AI\backend"))

from app.orchestration.models import ExecutionMode
from app.services.data_service import DataService
from app.services.feature_service import FeatureService
from app.services.insight_service import InsightService
from app.services.prediction_service import PredictionService
from app.services.decision_service import DecisionService
from app.services.simulation_service import SimulationService
from app.orchestration.engine import WorkflowEngine

import logging
logging.basicConfig(level=logging.INFO)

async def main():
    print("--- Booting Central Workflow Engine ---")
    data_svc = DataService()
    feat_svc = FeatureService()
    ins_svc = InsightService()
    pred_svc = PredictionService()
    dec_svc = DecisionService(data_svc, feat_svc, ins_svc, pred_svc)
    sim_svc = SimulationService()
    
    engine = WorkflowEngine(data_svc, feat_svc, ins_svc, pred_svc, dec_svc, sim_svc)
    
    # 1. STRICT MODE Execution
    print("\n[STRICT MODE] Executing Pipeline")
    state = await engine.execute_pipeline(
        session_id="SESS_9001",
        payload={"campaign": "Q4_Launch", "initial_budget": 50000},
        mode=ExecutionMode.STRICT
    )
    
    print("\n--- Pipeline State Output ---")
    print(state.model_dump_json(indent=2))
        
if __name__ == "__main__":
    asyncio.run(main())
