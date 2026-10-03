import logging
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings
from app.schemas.battery import BatteryAssessment

logger = logging.getLogger(__name__)


class BatteryAgent:
    """
    Domain agent responsible for analysing EV batteries.

    The agent performs domain-level assessment only.
    It does not make the final reuse/refurbish/recycle decision.
    """

    def __init__(self) -> None:
        self.chain = None
        if settings.groq_api_key and settings.groq_api_key.strip():
            try:
                self.llm = ChatGroq(
                    model=settings.groq_model,
                    api_key=settings.groq_api_key,
                    temperature=0,
                )

                self.structured_llm = self.llm.with_structured_output(
                    BatteryAssessment
                )

                self.prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            """
You are the Battery & Energy Storage Domain Agent
for CogniCycle EV, an AI-driven EV end-of-life
triage platform.

Your responsibility is to technically assess EV battery
assets using ONLY the information provided in the asset data.

Evaluate:

1. Battery condition
2. Technical and diagnostic indicators
3. Safety risks
4. Reuse potential
5. Refurbishment potential
6. Recycling considerations
7. Missing information
8. Additional evidence or tests required

Important rules:

- Do NOT invent missing values.
- Do NOT assume missing diagnostic information.
- Clearly identify missing or uncertain information.
- Treat safety-related information conservatively.
- High-voltage, thermal-risk, physical-damage, or safety-incident
  information must be explicitly reflected in the assessment.
- Use available SOH, SOC, cycle count, internal resistance,
  cell imbalance, thermal history, functional test results,
  physical condition, and economic information when present.
- Do not make a final system pathway decision.
- Do not output REUSE, REFURBISH, or RECYCLE as a final decision.
- Your role is to provide domain evidence for a later Decision Engine.
- Base confidence on the quality and completeness of the supplied evidence.
- Keep the reasoning technically grounded and concise.

The following metadata values are controlled by the application
and MUST be returned exactly:

agent_name:
"battery_agent"

domain:
"Battery & Energy Storage"

Do not change, rename, or reinterpret these values.

Return the result using the required BatteryAssessment schema.
""",
                        ),
                        (
                            "human",
                            """
Analyse the following EV battery asset.

Asset data:

{asset_data}
""",
                        ),
                    ]
                )

                self.chain = self.prompt | self.structured_llm
            except Exception as e:
                logger.warning(f"Could not initialize Groq chain: {e}")
                self.chain = None

    def _heuristic_assessment(self, asset: Dict[str, Any]) -> BatteryAssessment:
        """Domain heuristic fallback when LLM API is unavailable or unconfigured."""
        diag = asset.get("diagnostic_data") or {}
        safety = asset.get("safety_data") or {}
        tech = asset.get("technical_data") or {}

        soh = diag.get("soh")
        cycles = diag.get("cycle_count", 0)
        imbalance = diag.get("cell_imbalance", 0)
        ir = diag.get("internal_resistance", 0)
        phys_damage = (safety.get("physical_damage") or "none").lower()
        thermal_risk = (safety.get("thermal_risk") or "low").lower()
        has_thermal_runaway = bool(safety.get("thermal_runaway_history"))

        findings = []
        if soh is not None:
            findings.append(f"Diagnostic SOH recorded at {soh}%.")
        if cycles:
            findings.append(f"Cycle life usage: {cycles} cycles.")
        if imbalance:
            findings.append(f"Cell voltage imbalance: {imbalance} mV.")
        if ir:
            findings.append(f"Internal resistance: {ir} mOhm.")

        safety_risks = []
        if phys_damage not in ["none", "minor"]:
            safety_risks.append(f"Physical structural damage: {phys_damage}")
        if thermal_risk in ["high", "critical"]:
            safety_risks.append(f"High thermal runaway risk detected: {thermal_risk}")
        if has_thermal_runaway:
            safety_risks.append("Historical thermal runaway event on record.")

        if safety_risks:
            reuse_potential = "LOW"
            refurb_potential = "LOW"
        else:
            if soh is not None and soh >= 80:
                reuse_potential = "HIGH"
                refurb_potential = "MEDIUM"
            elif soh is not None and soh >= 65:
                reuse_potential = "MEDIUM"
                refurb_potential = "HIGH"
            else:
                reuse_potential = "LOW"
                refurb_potential = "LOW"

        chemistry = tech.get("technology", "Lithium-Ion")
        recycling = [
            f"Active cathode chemistry: {chemistry}.",
            "Recycle via hydrometallurgical processing for critical raw material recovery."
        ]

        missing = []
        if soh is None:
            missing.append("State of Health (SOH) diagnostic measurement missing")

        cond = asset.get("condition") or ("Good" if (soh and soh >= 80) else "Fair" if (soh and soh >= 65) else "Degraded")

        return BatteryAssessment(
            agent_name="battery_agent",
            domain="Battery & Energy Storage",
            assessment=f"Battery module ({chemistry}) assessed at {soh or 'unknown'}% SOH across {cycles} cycles.",
            condition_summary=cond,
            technical_findings=findings,
            safety_risks=safety_risks,
            reuse_potential=reuse_potential,
            refurbishment_potential=refurb_potential,
            recycling_considerations=recycling,
            missing_information=missing,
            evidence_requests=["Perform impedance spectroscopy"] if not ir else [],
            risk_flags=safety_risks,
            confidence=0.88 if soh is not None else 0.5,
            reasoning_summary=f"Assessment grounded in diagnostic SOH ({soh}%), cycle count ({cycles}), and safety data."
        )

    def analyze(self, asset: Dict[str, Any], use_llm: bool = False) -> BatteryAssessment:
        """
        Analyse a single battery asset and return a structured assessment.
        Fast domain heuristic is used by default during batch triage to save API calls.
        """
        if use_llm and self.chain:
            try:
                result = self.chain.invoke({"asset_data": asset})
                result.agent_name = "battery_agent"
                result.domain = "Battery & Energy Storage"
                return result
            except Exception as e:
                logger.warning(f"Groq LLM analysis failed ({e}), falling back to domain heuristic.")
                return self._heuristic_assessment(asset)

        return self._heuristic_assessment(asset)