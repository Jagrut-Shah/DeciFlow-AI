
import asyncio
import os
import sys
import json
import csv
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.orchestration.engine import WorkflowEngine
from app.core.result_store import ResultStore
from app.orchestration.models import PipelineState

async def verify():
    print("--- Starting Pipeline Verification ---")
    
    # 1. Load sample data
    data_path = "clothing_business_data.csv"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    print(f"Loading data from {data_path}...")
    raw_data = []
    with open(data_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_data.append(row)
            
    print(f"Loaded {len(raw_data)} records.")

    # 2. Initialize Engine using the factory to get all dependencies
    from app.core.dependencies import _build_workflow_engine
    engine = _build_workflow_engine()
    session_id = f"test_verify_{int(datetime.now().timestamp())}"
    
    print(f"Executing pipeline for session: {session_id}...")
    
    # 3. Execute
    try:
        final_state = await engine.execute_pipeline(session_id, raw_data)
        print("Pipeline execution completed.")
    except Exception as e:
        print(f"Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Check Results
    print("\n--- Results Analysis ---")
    print(f"Status: {final_state.status}")
    print(f"Total Steps: {len(final_state.steps)}")
    
    # Check Metrics
    if final_state.metrics:
        print("\nMetrics Extracted:")
        # Convert to dict for printing if it's a Pydantic model
        metrics_dict = final_state.metrics if isinstance(final_state.metrics, dict) else final_state.metrics.model_dump()
        print(json.dumps(metrics_dict, indent=2))
    else:
        print("\n[WARNING] No metrics extracted.")

    # Check Insights
    if final_state.insights:
        print(f"\nInsights Generated: {len(final_state.insights)}")
        for i, insight in enumerate(final_state.insights[:3]):
            insight_dict = insight if isinstance(insight, dict) else insight.model_dump()
            print(f"  {i+1}. {insight_dict.get('title', 'N/A')}: {insight_dict.get('narrative', 'N/A')[:100]}...")
    else:
        print("\n[WARNING] No insights generated.")

    # Check Decisions
    if final_state.decision:
        print("\nDecision Made:")
        decision_dict = final_state.decision if isinstance(final_state.decision, dict) else final_state.decision.model_dump()
        print(json.dumps(decision_dict, indent=2))
    else:
        print("\n[WARNING] No decision made.")

    # 5. Verify Persistence in ResultStore
    print("\n--- Persistence Verification ---")
    store = ResultStore()
    # Wait a bit for the async save to finish
    await asyncio.sleep(2) 
    
    db_path = "backend/data/db.json"
    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            db_data = json.load(f)
            if session_id in db_data:
                saved_state = db_data[session_id]["state"]
                print(f"SUCCESS: Session {session_id} found in db.json")
                print(f"Insights in DB: {len(saved_state.get('insights', []))}")
                print(f"Decision in DB: {saved_state.get('decision') is not None}")
            else:
                print(f"FAILURE: Session {session_id} NOT found in db.json")
                # print(f"Available sessions: {list(db_data.keys())[-3:]}")
    else:
        print(f"FAILURE: {db_path} does not exist.")

if __name__ == "__main__":
    asyncio.run(verify())

