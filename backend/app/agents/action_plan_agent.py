import json
import logging
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings
from app.schemas.action_plan import ActionStep, DynamicActionPlan
from app.schemas.asset import Asset

logger = logging.getLogger(__name__)


class ActionPlanAgent:
    """
    AI Agent that generates dynamic, deeply grounded circular economy action plans
    when triggered for a specific component.
    """

    def __init__(self) -> None:
        self.chain = None
        if settings.groq_api_key and settings.groq_api_key.strip():
            try:
                self.llm = ChatGroq(
                    model=settings.groq_model,
                    api_key=settings.groq_api_key,
                    temperature=0.2,
                    max_tokens=650,
                )
                self.structured_llm = self.llm.with_structured_output(DynamicActionPlan)
                self.prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            """You are an expert Circular Remanufacturing Engineer for CogniCycle EV.
Generate a grounded circular engineering protocol for the specified EV component.
Rules:
- Cite exact component name, manufacturer, model, weight in kg, and diagnostic metrics (SOH, cycles, impedance).
- economic_assumptions: 3 concise bullet points with net margins and Capex savings from provided economic figures.
- environmental_assumptions: 3 concise bullet points citing avoided embodied CO2e and conserved raw materials.
- action_steps: exactly 5 sequential operational steps. Titles concise, descriptions under 25 words.
Return strictly valid DynamicActionPlan.""",
                        ),
                        (
                            "human",
                            """Generate the circular action protocol for:
Component: {component_summary}
Disposition: {decision} ({confidence}) | Safety: {safety_status}
Rationale: {reasoning}
Financials: Reuse ${reuse_val}, Refurb ${refurb_val}, Repair ${repair_cost}, Testing ${test_cost}, Scrap ${recovery_val}
Weight: {weight_kg} kg | Tech: {technology}
Telemetry: SOH {soh}%, Cycles {cycles}, Internal Resistance {ir} mΩ""",
                        ),
                    ]
                )
                self.chain = self.prompt | self.structured_llm
            except Exception as e:
                logger.warning(f"Could not initialize ActionPlanAgent chain: {e}")
                self.chain = None

    def generate_plan(
        self,
        asset: Asset,
        decision: str,
        confidence: float = 0.85,
        safety_status: str = "SAFE",
        reasoning: str = ""
    ) -> DynamicActionPlan:
        """
        Produce a dynamic action plan by invoking the LLM with full component context.
        Falls back to a component-tailored heuristic plan if the LLM is unreachable or rate-limited.
        """
        asset_dict = asset.model_dump() if hasattr(asset, "model_dump") else dict(asset)
        
        if self.chain:
            try:
                diag = asset_dict.get("diagnostic_data") or {}
                tech = asset_dict.get("technical_data") or {}
                econ = asset_dict.get("economic_data") or {}

                comp_summary = f"{asset_dict.get('component')} ({asset_dict.get('manufacturer')} {asset_dict.get('model')}, {asset_dict.get('vehicle_make')} {asset_dict.get('vehicle_model')})"
                
                result = self.chain.invoke(
                    {
                        "component_summary": comp_summary,
                        "decision": decision,
                        "confidence": f"{int(confidence * 100)}%",
                        "safety_status": safety_status,
                        "reasoning": reasoning or "Evaluated by Decision Engine",
                        "reuse_val": econ.get("reuse_value", 0),
                        "refurb_val": econ.get("refurbishment_value", 0),
                        "repair_cost": econ.get("estimated_repair_cost", 0),
                        "test_cost": econ.get("estimated_testing_cost", 0),
                        "recovery_val": econ.get("recovery_value", 0),
                        "weight_kg": tech.get("weight_kg", 25),
                        "technology": tech.get("technology", "Automotive Grade"),
                        "soh": diag.get("soh", "N/A"),
                        "cycles": diag.get("cycle_count", "N/A"),
                        "ir": diag.get("internal_resistance", "N/A"),
                    }
                )
                return result
            except Exception as e:
                logger.warning(f"ActionPlanAgent LLM call failed ({e}), falling back to dynamic component heuristic.")
                return self._generate_dynamic_heuristic(asset_dict, decision, confidence, safety_status, reasoning)

        return self._generate_dynamic_heuristic(asset_dict, decision, confidence, safety_status, reasoning)

    def _generate_dynamic_heuristic(
        self,
        asset: Dict[str, Any],
        decision: str,
        confidence: float,
        safety_status: str,
        reasoning: str
    ) -> DynamicActionPlan:
        """
        Dynamically construct a component-grounded action plan using the asset's exact telemetry.
        """
        comp = asset.get("component") or "EV Component"
        mfr = asset.get("manufacturer") or "OEM"
        model = asset.get("model") or "Standard"
        vehicle = f"{asset.get('vehicle_make', '')} {asset.get('vehicle_model', '')}".strip() or "Electric Vehicle"
        tech = asset.get("technical_data") or {}
        diag = asset.get("diagnostic_data") or {}
        econ = asset.get("economic_data") or {}
        safety = asset.get("safety_data") or {}

        reuse_val = econ.get("reuse_value", 0)
        refurb_val = econ.get("refurbishment_value", 0)
        repair_cost = econ.get("estimated_repair_cost", 0)
        test_cost = econ.get("estimated_testing_cost", 0)
        logistics_cost = econ.get("estimated_logistics_cost", 0)
        recovery_val = econ.get("recovery_value", 0)
        net_margin = refurb_val - (repair_cost + test_cost + logistics_cost)

        soh = diag.get("soh")
        cycles = diag.get("cycle_count", 0)
        chem = tech.get("technology") or tech.get("material") or "Advanced E-Drive Materials"

        if decision == "REFURBISH":
            headline = f"Engineering Refurbishment & Reconditioning Protocol for {mfr} {model} ({comp}) from {vehicle}"
            econ_assumptions = [
                f"Gross Refurbishment Value: ${refurb_val:,.2f} with direct repair/testing expenditure of ${repair_cost + test_cost:,.2f}.",
                f"Projected net margin of ${max(net_margin, 120):,.2f} per unit for {comp} ({mfr} {model}).",
                f"Delivers ~65% cost savings for {vehicle} fleet operators compared to new OEM procurement.",
                "Target remanufacturing turnaround cycle: 10-12 days to maximize inventory velocity."
            ]
            env_assumptions = [
                f"Avoids ~{max(int((tech.get('weight_kg', 10) * 4.5)), 45)} kg of embodied CO2e emissions vs primary production of a new {comp}.",
                f"Conserves critical materials ({chem}) and prevents landfilling of high-grade copper and alloys.",
                "Energy consumption during reconditioning is <14% of virgin smelting/refining energy.",
                "100% of rejected sub-elements are routed to certified closed-loop metallurgical recyclers."
            ]
            steps = [
                ActionStep(step=1, title=f"Inbound De-energization & Housing Disassembly for {comp}", description=f"Safely isolate electrical buses on the {mfr} {model}, discharge residual capacitance, and inspect exterior enclosure."),
                ActionStep(step=2, title="Subsystem Fault & Telemetry Diagnostic Isolation", description=f"Run parametric bench diagnostics verifying {comp} health (recorded SOH: {soh or 'N/A'}%, cycles: {cycles}). Locate compromised subcomponents."),
                ActionStep(step=3, title="Precision Reconditioning & Subcomponent Renewal", description=f"Replace fatigued contact points, renew thermal interface pastes, and re-solder joints using lead-free alloys."),
                ActionStep(step=4, title="Dynamic Load & Thermal-Electric Stress Testing", description=f"Simulate operational load cycles matching {vehicle} specifications to verify power output and thermal equilibrium."),
                ActionStep(step=5, title="Digital Product Passport (DPP) Certification & Dispatch", description=f"Encode renewed operational tolerances and warranty certificate onto RFID/QR tag for distribution to certified EV repair centers.")
            ]

        elif decision == "REUSE":
            headline = f"Direct Second-Life & Re-Deployment Protocol for {mfr} {model} ({comp})"
            econ_assumptions = [
                f"Direct Asset Realization: Captures up to ${reuse_val:,.2f} in immediate secondary market value.",
                f"Minimal processing overhead: Cleaning and qualification testing limited to ${test_cost + logistics_cost:,.2f}.",
                "Net operating margin exceeding 85% with immediate cash conversion into secondary storage/spares.",
                f"High commercial viability in stationary storage or secondary replacement for {vehicle} platforms."
            ]
            env_assumptions = [
                f"Maximal lifecycle decarbonization: 95%+ embodied carbon extension for this {mfr} {model}.",
                f"Completely eliminates virgin raw material extraction ({chem}) required for a replacement unit.",
                "Extends the operational circular lifetime by an estimated 6 to 10 additional calendar years.",
                "Diverts functional high-performance systems from premature thermal shredding."
            ]
            steps = [
                ActionStep(step=1, title="Precision Surface Cleaning & Connector Conditioning", description=f"Perform ultrasonic dry-ice decontamination on terminals and check mechanical mounting tabs of {mfr} {model}."),
                ActionStep(step=2, title="Full Parametric & Capacity Re-verification", description=f"Verify baseline performance (measured SOH: {soh or 'nominal'}%) and confirm insulation resistance exceeds 500 MOhm."),
                ActionStep(step=3, title="Firmware Calibration & Fault Register Clear", description=f"Interrogate non-volatile memory, reset historical DTC error codes, and configure operating profile for second-life duty."),
                ActionStep(step=4, title="Modular Second-Life Protective Enclosure", description=f"Mount {comp} into standardized modular rack or protective transit chassis with shock isolation."),
                ActionStep(step=5, title="Dispatch to Verified Circular Partner", description=f"Deliver component to certified BESS storage integrator or verified EV aftermarket remanufacturer.")
            ]

        elif decision == "RECYCLE":
            headline = f"Closed-Loop Material Recovery & Hydrometallurgical Protocol for {mfr} {model} ({comp})"
            econ_assumptions = [
                f"Critical Mineral Reclamation: Estimated recoverable commodity value of ${recovery_val:,.2f} ({chem}).",
                f"Protects domestic supply chain against price volatility for lithium, nickel, cobalt, copper, or rare-earth elements.",
                "Avoids significant regulatory EPR non-compliance penalties and hazardous disposal fees.",
                "High extraction efficiency (>95%) feeds high-purity precursor materials back into gigafactories."
            ]
            env_assumptions = [
                "Reduces freshwater consumption by up to 80% compared to primary brine and open-pit ore extraction.",
                f"Safely neutralizes hazardous substances associated with {comp} before chemical leaching.",
                "Delivers 50-70% reduction in greenhouse gas emissions compared to primary mineral smelting.",
                "Ensures 100% digital trace compliance under hazardous e-waste handling mandates."
            ]
            steps = [
                ActionStep(step=1, title="Total Neutralization & Deep Discharge", description=f"Bring {mfr} {model} to absolute 0.0V using resistive load sink or liquid salt-bath immersion to eliminate electrical hazards."),
                ActionStep(step=2, title="Inert Atmosphere Shredding & Mechanical Pre-treatment", description=f"Dismantle external casing of {comp}; shred cell stacks/modules under a nitrogen blanket to prevent oxidation and runaway."),
                ActionStep(step=3, title="Multi-Stage Density & Magnetic Classification", description="Separate ferrous structural steel, aluminum foils, copper collector plates, and plastic polymers."),
                ActionStep(step=4, title="Hydrometallurgical Acid Leaching & Purification", description=f"Dissolve active Black Mass into sulfate solutions; selectively precipitate high-purity battery/metal precursors."),
                ActionStep(step=5, title="Circular Supply Chain Manifesting", description=f"Log certified chemical assay data and dispatch reclaimed precursors directly to domestic battery/motor manufacturers.")
            ]

        else:  # ASSESSMENT_REQUIRED
            headline = f"Specialized Diagnostic Triage & Laboratory Protocol for {mfr} {model} ({comp})"
            econ_assumptions = [
                f"Downside Risk Mitigation: Prevents premature scrapping of high-value assembly (potential recovery: ${refurb_val or reuse_val:,.2f}).",
                f"Targeted diagnostic investment (${test_cost or 75:,.2f}) protects against scrap loss and dangerous field failures.",
                "Ensures facility and workforce safety by identifying hidden internal faults prior to handling.",
                "Establishes empirical business case to decide between refurbishment vs closed-loop material reclamation."
            ]
            env_assumptions = [
                "Hazardous incident prevention: Eliminates spontaneous thermal or short-circuit events during processing.",
                "Guarantees that salvageable circular components are not needlessly downcycled into smelting furnaces.",
                "Directs the component to the single most carbon-efficient destination upon test completion."
            ]
            steps = [
                ActionStep(step=1, title="Safety Quarantine & Continuous Telemetry Logging", description=f"Place the {mfr} {model} in an isolated bay with 24-hour infrared thermal tracking and gas monitoring."),
                ActionStep(step=2, title="Advanced Non-Destructive Scanning (EIS & CT)", description=f"Conduct multi-frequency Electrochemical Impedance Spectroscopy and industrial X-ray tomography to detect internal defects."),
                ActionStep(step=3, title="Onboard Controller Interrogation", description=f"Connect directly to diagnostic ports to retrieve lifetime thermal excursions, over-current events, and internal DTC logs."),
                ActionStep(step=4, title="Techno-Economic Feasibility Review", description=f"Evaluate newly verified physical parameters against live secondary market price indices to determine optimal disposition."),
                ActionStep(step=5, title="Definitive Re-classification & Routing", description=f"Update CogniCycle EV registry with finalized empirical triage result and transfer to designated processing line.")
            ]

        return DynamicActionPlan(
            disposition=decision,
            headline=headline,
            economic_assumptions=econ_assumptions,
            environmental_assumptions=env_assumptions,
            action_steps=steps
        )
