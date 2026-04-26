from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Any, Dict
from app.core.dependencies import get_data_service
from app.domain.interfaces.data_service import IDataService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    data_svc: IDataService = Depends(get_data_service)
) -> Dict[str, Any]:
    """
    Uploads a CSV or JSON file and parses its contents.
    """
    logger.info(f"Received upload request for file: {file.filename}")
    
    content = await file.read()
    
    if file.filename.endswith(".csv"):
        parsed_data = data_svc.parse_csv_content(content)
    elif file.filename.endswith(".json"):
        parsed_data = data_svc.parse_json_content(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload .csv or .json")

    if "error" in parsed_data:
        raise HTTPException(status_code=422, detail=f"Parsing error: {parsed_data['error']}")

    # Use process_raw_data to sanitize and extract metrics
    # Note: process_raw_data expects a payload, but here we might have a list of records.
    # For simplicity, we return the parsed data and a preview.
    
    records = parsed_data.get("data", [])
    if isinstance(parsed_data, dict) and not records:
        # If it was a single dict (JSON object), wrap it
        records = [parsed_data] if parsed_data else []

    return {
        "status": "success",
        "filename": file.filename,
        "record_count": len(records),
        "preview": records[:5],
        "message": "File parsed successfully."
    }
