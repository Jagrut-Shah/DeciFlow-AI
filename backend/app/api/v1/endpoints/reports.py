import logging
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any

from app.services.report_service import ReportService

router = APIRouter()
report_service = ReportService(output_dir="exports")

class ReportRequest(BaseModel):
    session_id: str
    data: Dict[str, Any]

@router.post("/generate")
async def generate_report(request: ReportRequest):
    """
    Generates a PDF report and returns the filepath.
    """
    try:
        # Detect if it's an Intelligence report (has 'stats') or a Simulation report
        if "stats" in request.data:
            filepath = report_service.generate_intelligence_report(request.data)
        else:
            filepath = report_service.generate_simulation_report(request.session_id, request.data)
            
        filename = os.path.basename(filepath)
        return {
            "status": "success",
            "data": {
                "session_id": request.session_id,
                "report_url": f"/api/v1/reports/download/{filename}",
                "filename": filename
            }
        }
    except Exception as e:
        logging.error(f"Error in generate_report endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Downloads a previously generated PDF report.
    """
    filepath = os.path.join("exports", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=filename
    )
