from fastapi import APIRouter, HTTPException

from app.schemas.asset import Asset
from app.schemas.battery import BatteryAssessment
from app.services.battery_service import BatteryService


router = APIRouter(
    prefix="/battery",
    tags=["Battery"],
)

battery_service = BatteryService()


@router.post(
    "/analyze",
    response_model=BatteryAssessment,
)
def analyze_battery(asset: Asset) -> BatteryAssessment:
    """
    Analyse a single EV battery asset.
    """

    try:
        return battery_service.analyze_asset(asset.model_dump())

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Battery analysis failed.",
        ) from exc