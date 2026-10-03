from typing import List, Optional
from pydantic import BaseModel, Field


class BatteryAssessment(BaseModel):
    """Structured assessment produced by the Battery Domain Agent."""

    agent_name: str = Field(
        default="battery_agent",
        description="Name of the domain agent that produced the assessment."
    )

    domain: str = Field(
        default="Battery & Energy Storage",
        description="EV e-waste domain being assessed."
    )

    assessment: str = Field(
        description="Overall technical assessment of the battery."
    )

    condition_summary: str = Field(
        description="Summary of the battery's observed condition."
    )

    technical_findings: List[str] = Field(
        default_factory=list,
        description="Important technical findings from the available diagnostic data."
    )

    safety_risks: List[str] = Field(
        default_factory=list,
        description="Identified battery safety risks."
    )

    reuse_potential: str = Field(
        description="Assessment of whether the battery may be suitable for reuse."
    )

    refurbishment_potential: str = Field(
        description="Assessment of whether refurbishment may be technically viable."
    )

    recycling_considerations: List[str] = Field(
        default_factory=list,
        description="Important considerations if the battery proceeds toward recycling."
    )

    missing_information: List[str] = Field(
        default_factory=list,
        description="Information that is missing and materially limits the assessment."
    )

    evidence_requests: List[str] = Field(
        default_factory=list,
        description="Additional evidence or tests that should be obtained."
    )

    risk_flags: List[str] = Field(
        default_factory=list,
        description="Important flags requiring attention."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the assessment based on available evidence."
    )

    reasoning_summary: str = Field(
        description="Concise explanation connecting the available evidence to the assessment."
    )