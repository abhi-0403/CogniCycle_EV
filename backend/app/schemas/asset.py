from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class Asset(BaseModel):
    """
    Canonical EV asset representation.

    The schema is intentionally flexible because different EV
    components expose different technical and diagnostic fields.
    """

    model_config = ConfigDict(extra="allow")

    asset_id: Optional[str] = None
    component: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    vehicle: Optional[str] = None
    condition: Optional[str] = None

    technical_data: Optional[Dict[str, Any]] = None
    diagnostic_data: Optional[Dict[str, Any]] = None
    safety_data: Optional[Dict[str, Any]] = None
    economic_data: Optional[Dict[str, Any]] = None