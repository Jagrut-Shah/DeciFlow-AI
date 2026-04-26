"""
DataService — Pipeline Step 1
------------------------------
Validates and normalizes inbound raw payload using DataAgent for business logic.
"""

import csv
import json
import io
import logging

from typing import Any, Dict
from app.domain.interfaces.data_service import IDataService
from app.observability.metrics import metrics

logger = logging.getLogger(__name__)


class DataService(IDataService):

    def parse_csv_content(self, content: bytes) -> Dict[str, Any]:
        """Parses raw CSV bytes into a dictionary with a 'data' list."""
        try:
            content_str = content.decode("utf-8", errors="ignore")
            f = io.StringIO(content_str)
            reader = csv.DictReader(f)
            return {"data": list(reader)}
        except Exception as e:
            logger.error(f"DataService: CSV parsing failed: {e}")
            return {"data": [], "error": str(e)}

    def parse_json_content(self, content: bytes) -> Dict[str, Any]:
        """Parses raw JSON bytes into a dictionary with a 'data' list."""
        try:
            content_str = content.decode("utf-8", errors="ignore")
            parsed = json.loads(content_str)
            if isinstance(parsed, list):
                return {"data": parsed}
            elif isinstance(parsed, dict):
                if "data" in parsed:
                    return parsed
                return {"data": [parsed]}
            return {"data": []}
        except Exception as e:
            logger.error(f"DataService: JSON parsing failed: {e}")
            return {"data": [], "error": str(e)}

    async def process_raw_data(self, source: str, payload: Any) -> Dict[str, Any]:
        """
        Ingests and cleans raw data from any source (bytes, list, or dict).
        """
        metrics.increment("pipeline_data_total")
        raw_records = []
        
        # 1. Handle bytes (raw file upload)
        if isinstance(payload, bytes):
            # Try JSON first
            parse_result = self.parse_json_content(payload)
            raw_records = parse_result.get("data", [])
            
            # If JSON failed or returned nothing, try CSV
            if not raw_records:
                parse_result = self.parse_csv_content(payload)
                raw_records = parse_result.get("data", [])
        
        # 2. Handle structured objects
        elif isinstance(payload, list):
            raw_records = payload
        elif isinstance(payload, dict):
            raw_records = payload.get("data", [payload] if payload else [])
        
        # 3. Guard against empty data
        if not raw_records:
            logger.warning(f"DataService: No records found from '{source}'.")
            return {
                "source": source or "unknown",
                "record_count": 0,
                "fields": [],
                "raw": {},
                "_fallback": True,
            }

        # 4. BRIDGE: Route to DataAgent for actual business logic
        from app.agents.data_agent import DataAgent
        agent = DataAgent()
        
        # Execute the agent
        agent_result = await agent.execute({"data": raw_records})
        
        if agent_result.get("status") != "ok":
            logger.error(f"DataService: DataAgent failed: {agent_result.get('error')}")
            return {
                "source": source,
                "record_count": len(raw_records),
                "fields": list(raw_records[0].keys()) if raw_records else [],
                "raw": raw_records[0] if raw_records else {},
                "_fallback": True,
            }

        processed_data = agent_result.get("processed_data", [])
        metrics_data = agent_result.get("metrics", {})
        metadata = agent_result.get("metadata", {})

        return {
            "source": source,
            "record_count": metadata.get("processed_record_count", len(processed_data)),
            "fields": metadata.get("fields_detected", []),
            "processed_data": processed_data,
            "metrics": metrics_data,
            "category_performance": agent_result.get("category_performance", {}),
            "data_quality": agent_result.get("data_quality", 100),
            "raw": processed_data[0] if processed_data else {},
            "_fallback": False,
        }
