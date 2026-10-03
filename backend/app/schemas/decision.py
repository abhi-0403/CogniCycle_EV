from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DecisionResult(BaseModel):
    """
    Generic decision schema for the final output of the Decision Engine.
    """
    
    asset_id: Optional[str] = Field(None, description="The unique asset ID")
    component: Optional[str] = Field(None, description="The evaluated component name")
    domain: str = Field(..., description="The domain the asset was routed to")
    
    # REUSE, REFURBISH, RECYCLE, ASSESSMENT_REQUIRED
    decision: str = Field(..., description="The final circular-economy pathway")
    confidence: float = Field(..., description="Confidence level in the decision (0.0 to 1.0)")
    
    evidence: List[str] = Field(default_factory=list, description="Key evidence supporting the decision")
    safety_status: str = Field(..., description="Safety status evaluation (e.g., SAFE, CRITICAL_RISK)")
    economic_summary: Optional[str] = Field(None, description="Summary of economic viability")
    
    missing_information: List[str] = Field(default_factory=list, description="Critical information missing for decision")
    reasoning: str = Field(..., description="Detailed explanation of why the pathway was selected")
    
    agent_assessment: Optional[Dict[str, Any]] = Field(None, description="The raw domain agent assessment output")
    action_plan: Optional[Dict[str, Any]] = Field(None, description="Grounded operational steps, environmental assumptions, and economic assumptions")
