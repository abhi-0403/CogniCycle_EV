import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.battery import BatteryAssessment

logger = logging.getLogger(__name__)


class UniversalAssessment(BaseModel):
    agent_name: str = Field(default="universal_triage_agent")
    domain: str = Field(...)
    assessment: str = Field(...)
    condition_summary: str = Field(...)
    technical_findings: List[str] = Field(default_factory=list)
    safety_risks: List[str] = Field(default_factory=list)
    reuse_potential: str = Field(default="HIGH")
    refurbishment_potential: str = Field(default="MEDIUM")
    recycling_considerations: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    evidence_requests: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.88)
    reasoning_summary: str = Field(...)


class UniversalTriageAgent:
    """
    Universal Domain Agent for CogniCycle EV across all 7 pillars of EV components:
    1. Battery & Energy Storage (Packs, modules, cells, BMS)
    2. Electric Drive Systems (PMSM, Induction motors, rotors, stators, bearings)
    3. Power Electronics (Traction Inverters, DC-DC, IGBTs, SiC modules)
    4. Charging Electronics (On-board chargers, charge controllers, contactors)
    5. Control & Computing (Gateway ECUs, Vehicle Control Units, ADAS compute)
    6. Sensors & Communication (Radars, LiDAR, Cameras, CAN transceivers)
    7. Auxiliary Electronics (e-Compressors, heat pumps, power steering units)
    """

    def __init__(self) -> None:
        self.chain = None

    def _heuristic_assessment(self, asset: Dict[str, Any], domain: str) -> UniversalAssessment:
        """Deterministic domain heuristic assessment covering all 7 EV subsystem pillars."""
        diag = asset.get("diagnostic_data") or {}
        safety = asset.get("safety_data") or {}
        tech = asset.get("technical_data") or {}
        comp = asset.get("component") or "EV Component"
        mfr = asset.get("manufacturer") or "OEM"
        model = asset.get("model") or ""

        soh = diag.get("soh")
        cycles = diag.get("cycle_count", 0)
        imbalance = diag.get("cell_imbalance", 0)
        ir = diag.get("internal_resistance", 0)
        func_result = str(diag.get("functional_test_result") or "pass").lower()
        error_codes = diag.get("error_codes") or diag.get("fault_codes") or []

        phys_damage = str(safety.get("physical_damage") or "none").lower()
        thermal_risk = str(safety.get("thermal_risk") or "low").lower()
        has_runaway = bool(safety.get("thermal_runaway_history"))

        findings = []
        if soh is not None:
            findings.append(f"Diagnostic State of Health (SOH): {soh}%.")
        if cycles:
            findings.append(f"Recorded lifecycle utilization: {cycles:,} cycles.")
        if ir:
            findings.append(f"Measured internal impedance: {ir} mΩ.")
        if imbalance:
            findings.append(f"Cell group imbalance delta: {imbalance} mV.")
        if error_codes:
            findings.append(f"Active diagnostic trouble codes (DTCs): {', '.join(error_codes)}.")
        else:
            findings.append("No active DTCs or critical faults logged in non-volatile register.")

        # Safety hazards screening (Only genuine thermal/structural hazards, NOT normal EV high voltage)
        safety_risks = []
        if has_runaway:
            safety_risks.append("Historical thermal runaway event on record.")
        if phys_damage in ["severe", "crushed", "puncture", "heavy"]:
            safety_risks.append(f"Severe physical structural compromise: {phys_damage}")
        if thermal_risk in ["critical", "high"]:
            safety_risks.append(f"Elevated thermal runaway risk: {thermal_risk}")

        # Assess potential based on domain and telemetry
        if safety_risks:
            reuse_potential = "LOW"
            refurb_potential = "LOW"
            cond = "Degraded"
        elif soh is not None and soh >= 80:
            reuse_potential = "HIGH"
            refurb_potential = "MEDIUM"
            cond = "Good" if soh < 90 else "Excellent"
        elif soh is not None and soh >= 65:
            reuse_potential = "MEDIUM"
            refurb_potential = "HIGH"
            cond = "Fair"
        elif soh is not None and soh < 65:
            reuse_potential = "LOW"
            refurb_potential = "LOW"
            cond = "Degraded"
        else:
            # Non-battery components (Inverters, Motors, OBCs, ECUs)
            if func_result in ["pass", "nominal"] and phys_damage in ["none", "minor"]:
                reuse_potential = "HIGH"
                refurb_potential = "MEDIUM"
                cond = "Good"
            elif func_result in ["degraded", "recalibration_required"] or phys_damage == "moderate":
                reuse_potential = "MEDIUM"
                refurb_potential = "HIGH"
                cond = "Fair"
            else:
                reuse_potential = "LOW"
                refurb_potential = "LOW"
                cond = "Degraded"

        technology = tech.get("technology") or tech.get("semiconductor_type") or "Automotive Grade"
        recycling = [
            f"Subsystem domain: {domain} ({technology}).",
            "Closed-loop metallurgical and electronic component recovery stream."
        ]

        return UniversalAssessment(
            agent_name="universal_triage_agent",
            domain=domain,
            assessment=f"{comp} ({mfr} {model}) assessed under {domain} standards. Condition: {cond}.",
            condition_summary=cond,
            technical_findings=findings,
            safety_risks=safety_risks,
            reuse_potential=reuse_potential,
            refurbishment_potential=refurb_potential,
            recycling_considerations=recycling,
            missing_information=[],
            evidence_requests=[],
            risk_flags=safety_risks,
            confidence=0.92 if soh is not None or func_result == "pass" else 0.75,
            reasoning_summary=f"Technical telemetry indicates {cond.lower()} operational state with {reuse_potential.lower()} direct second-life suitability."
        )

    def analyze(self, asset: Dict[str, Any], domain: str = "Battery & Energy Storage", use_llm: bool = False) -> UniversalAssessment:
        """Analyze any component across all 7 pillars of EV technology."""
        return self._heuristic_assessment(asset, domain)
