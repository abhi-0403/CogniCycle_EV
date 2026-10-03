from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.asset import Asset


class ActionStep(BaseModel):
    step: int = Field(..., description="Step sequence number (1-5)")
    title: str = Field(..., description="Specific action title")
    description: str = Field(..., description="Detailed technical procedure tailored to this component")


class DynamicActionPlan(BaseModel):
    disposition: str = Field(..., description="Disposition pathway: REUSE, REFURBISH, RECYCLE, or ASSESSMENT_REQUIRED")
    headline: str = Field(..., description="Tailored protocol headline for this specific component")
    economic_assumptions: List[str] = Field(..., description="Component-specific economic assumptions and margins")
    environmental_assumptions: List[str] = Field(..., description="Component-specific environmental assumptions and decarbonization metrics")
    action_steps: List[ActionStep] = Field(..., description="Sequenced operational steps tailored to this component")
    is_cached: Optional[bool] = Field(default=False, description="Whether this plan was retrieved from persistent cache without LLM call")


class ActionPlanRequest(BaseModel):
    asset: Asset
    decision: str
    confidence: Optional[float] = 0.85
    safety_status: Optional[str] = "SAFE"
    reasoning: Optional[str] = None
    force_regenerate: bool = False
