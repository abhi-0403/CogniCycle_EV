import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.schemas.action_plan import ActionPlanRequest, DynamicActionPlan
from app.schemas.asset import Asset
from app.schemas.decision import DecisionResult
from app.services.action_plan_service import ActionPlanService
from app.services.ingestion_service import IngestionService
from app.services.pipeline_service import PipelineService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/assets", tags=["assets"])

ingestion_service = IngestionService()
pipeline_service = PipelineService()
action_plan_service = ActionPlanService()
storage_service = StorageService()


class UploadDatasetPayload(BaseModel):
    filename: Optional[str] = "custom_dataset.json"
    assets: List[Dict[str, Any]]


@router.get("", response_model=List[Asset])
def get_assets():
    """Retrieve all operational assets from the input dataset."""
    try:
        return ingestion_service.load_assets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/triage")
def get_triage_results():
    """
    Get full triage decisions for all assets.
    If backend/data/output/analyzed_assets.json exists, returns the cached file instantly (0 delays, 0 LLM calls).
    If output was deleted or doesn't exist, executes the analysis, persists to disk, and returns the results.
    """
    try:
        cached = storage_service.load_analyzed_assets()
        if cached:
            return {
                "source": "cache",
                "count": len(cached),
                "data": cached
            }

        # Otherwise, run analysis once on the input dataset and persist to backend/data/output/
        raw_assets = ingestion_service.load_assets()
        analyzed = pipeline_service.process_all_assets(raw_assets)
        storage_service.save_analyzed_assets(analyzed)

        return {
            "source": "analyzed_fresh",
            "count": len(analyzed),
            "data": analyzed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/triage/rerun")
def rerun_triage():
    """Force re-run the triage pipeline across the current dataset and update cached output."""
    try:
        raw_assets = ingestion_service.load_assets()
        analyzed = pipeline_service.process_all_assets(raw_assets)
        storage_service.save_analyzed_assets(analyzed)
        return {
            "status": "success",
            "message": f"Successfully re-analyzed {len(analyzed)} assets and saved to output folder.",
            "data": analyzed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_dataset_file(file: UploadFile = File(None)):
    """Upload a custom JSON file of EV assets from the frontend to triage."""
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded.")

        content = await file.read()
        try:
            data = json.loads(content.decode("utf-8"))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON file format.")

        if not isinstance(data, list):
            # Check if wrapped in an object
            if isinstance(data, dict) and "assets" in data and isinstance(data["assets"], list):
                data = data["assets"]
            else:
                raise HTTPException(status_code=400, detail="JSON must contain a list of EV asset objects.")

        if len(data) == 0:
            raise HTTPException(status_code=400, detail="Uploaded dataset contains 0 items.")

        # Persist uploaded file to input directory
        storage_service.save_uploaded_dataset(data)

        # Convert to Pydantic Asset models
        parsed_assets = [Asset(**item) for item in data]

        # Analyze dataset and persist output
        analyzed = pipeline_service.process_all_assets(parsed_assets)
        storage_service.save_analyzed_assets(analyzed)

        return {
            "status": "success",
            "filename": file.filename,
            "count": len(analyzed),
            "data": analyzed
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-json")
def upload_dataset_json(payload: UploadDatasetPayload):
    """Direct JSON payload upload from frontend FileReader."""
    try:
        if not payload.assets or len(payload.assets) == 0:
            raise HTTPException(status_code=400, detail="Asset list cannot be empty.")

        # Persist uploaded file to input directory
        storage_service.save_uploaded_dataset(payload.assets)

        # Parse & run pipeline
        parsed_assets = [Asset(**item) for item in payload.assets]
        analyzed = pipeline_service.process_all_assets(parsed_assets)
        storage_service.save_analyzed_assets(analyzed)

        return {
            "status": "success",
            "filename": payload.filename,
            "count": len(analyzed),
            "data": analyzed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=DecisionResult)
def analyze_asset(asset: Asset):
    """Process a single asset through the end-to-end pipeline."""
    try:
        return pipeline_service.process_asset(asset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/action-plan", response_model=DynamicActionPlan)
def generate_action_plan(request: ActionPlanRequest):
    """
    Dynamically invoke LLM with specific component context when Take Action is clicked.
    Uses cached plan if already generated, saving LLM calls.
    """
    try:
        return action_plan_service.generate_plan(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/action-plans")
def get_all_action_plans():
    """Retrieve all cached action plans."""
    return action_plan_service.get_all_plans()


@router.delete("/output")
def clear_output_storage():
    """Explicitly delete the backend/data/output folder to restart analysis from scratch."""
    success = storage_service.clear_output()
    return {
        "status": "cleared" if success else "error",
        "message": "Output folder cleared. Next triage request will re-analyze from scratch."
    }
