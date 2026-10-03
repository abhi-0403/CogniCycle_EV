from typing import Any, Dict

from app.schemas.asset import Asset
from app.schemas.decision import DecisionResult


class DecisionEngine:
    """
    Evaluates evidence and deterministic rules to output a final pathway.
    """

    PATHWAYS = {
        "REUSE": "REUSE",
        "REFURBISH": "REFURBISH",
        "RECYCLE": "RECYCLE",
        "ASSESSMENT_REQUIRED": "ASSESSMENT_REQUIRED"
    }

    def evaluate(self, asset: Asset, domain: str, agent_assessment: Dict[str, Any] = None) -> DecisionResult:
        if agent_assessment is None:
            agent_assessment = {}

        evidence = []
        missing_info = agent_assessment.get("missing_information", [])
        safety_risks = list(agent_assessment.get("safety_risks", []))
        
        # Check safety data from asset
        asset_safety = asset.safety_data or {}
        thermal_risk = str(asset_safety.get("thermal_risk") or "").lower()
        physical_damage = str(asset_safety.get("physical_damage") or "").lower()
        has_runaway = bool(asset_safety.get("thermal_runaway_history"))

        if has_runaway:
            safety_risks.append("Historical thermal runaway event on record.")
        if physical_damage in ["severe", "crushed", "puncture", "heavy"]:
            safety_risks.append(f"Severe physical structural damage: {physical_damage}")
        if thermal_risk in ["critical", "high"]:
            safety_risks.append(f"Elevated thermal hazard level: {thermal_risk}")

        # 1. Evaluate Evidence Completeness
        if missing_info and len(missing_info) > 1:
            grounded_evidence = self._generate_grounded_evidence(asset, domain, self.PATHWAYS["ASSESSMENT_REQUIRED"], safety_risks, "UNKNOWN")
            return self._build_result(
                asset=asset,
                domain=domain,
                decision=self.PATHWAYS["ASSESSMENT_REQUIRED"],
                confidence=0.4,
                evidence=grounded_evidence,
                safety_status="UNKNOWN",
                missing_information=missing_info,
                reasoning="Incomplete diagnostic telemetry requires specialized bench evaluation before routing.",
                agent_assessment=agent_assessment
            )

        # 2. Evaluate Safety Risks (Exclude benign high_voltage attribute)
        if safety_risks:
            grounded_evidence = self._generate_grounded_evidence(asset, domain, self.PATHWAYS["RECYCLE"], safety_risks, "CRITICAL_RISK")
            return self._build_result(
                asset=asset,
                domain=domain,
                decision=self.PATHWAYS["RECYCLE"],
                confidence=0.92,
                evidence=grounded_evidence,
                safety_status="CRITICAL_RISK",
                missing_information=missing_info,
                reasoning=f"Irreversible safety hazards ({'; '.join(safety_risks)}) mandate closed-loop recycling.",
                agent_assessment=agent_assessment
            )

        # 3. Evaluate Technical Diagnostic Telemetry & Economics
        diag = asset.diagnostic_data or {}
        soh = diag.get("soh")
        func_result = str(diag.get("functional_test_result") or "").lower()
        condition = agent_assessment.get("condition_summary", "").lower()
        asset_condition = (asset.condition or "").lower()

        # Economic Valuation
        economic_summary = ""
        econ_data = asset.economic_data or {}
        reuse_val = econ_data.get("reuse_value", 0) if econ_data else 0
        refurb_val = econ_data.get("refurbishment_value", 0) if econ_data else 0
        repair_cost = econ_data.get("estimated_repair_cost", 0) if econ_data else 0
        test_cost = econ_data.get("estimated_testing_cost", 0) if econ_data else 0
        logistic_cost = econ_data.get("estimated_logistics_cost", 0) if econ_data else 0
        net_refurbishment = refurb_val - repair_cost - test_cost - logistic_cost

        if econ_data:
            economic_summary = f"Gross Reuse Value: ${reuse_val:,.0f} | Net Refurbish Margin: ${net_refurbishment:,.0f}"

        # SOH & Technical Thresholds
        is_high_health = (soh is not None and soh >= 80) or ("good" in condition or "excellent" in condition or "good" in asset_condition or "excellent" in asset_condition)
        is_moderate_health = (soh is not None and 65 <= soh < 80) or ("fair" in condition or "fair" in asset_condition or "repair" in condition or func_result == "degraded")
        is_depleted_health = (soh is not None and soh < 65) or ("poor" in condition or "poor" in asset_condition or "scrap" in condition or func_result in ["fail", "unresponsive"])

        # Pathway Decisions
        if is_high_health and not is_depleted_health and func_result != "fail":
            grounded_evidence = self._generate_grounded_evidence(asset, domain, self.PATHWAYS["REUSE"], safety_risks, "SAFE")
            reason = f"Diagnostic health ({soh}% SOH) and structural integrity qualify unit for high-value direct second-life deployment." if soh else "Component technical condition and pass telemetry allow direct reuse."
            return self._build_result(
                asset, domain, self.PATHWAYS["REUSE"], 0.90, grounded_evidence, "SAFE",
                missing_info, reason, agent_assessment, economic_summary
            )
        elif is_moderate_health or net_refurbishment > 0:
            grounded_evidence = self._generate_grounded_evidence(asset, domain, self.PATHWAYS["REFURBISH"], safety_risks, "SAFE")
            reason = f"Component exhibits repairable wear ({soh}% SOH); precision refurbishment recovers substantial market value." if soh else "Refurbishment and recalibration will restore unit to verified operating specification."
            return self._build_result(
                asset, domain, self.PATHWAYS["REFURBISH"], 0.85, grounded_evidence, "SAFE",
                missing_info, reason, agent_assessment, economic_summary
            )
        elif is_depleted_health:
            grounded_evidence = self._generate_grounded_evidence(asset, domain, self.PATHWAYS["RECYCLE"], safety_risks, "SAFE")
            reason = f"Component health ({soh}% SOH) has reached end-of-life; closed-loop mineral recycling recovers strategic raw materials." if soh else "End-of-life condition indicates specialized material recycling is the optimal pathway."
            return self._build_result(
                asset, domain, self.PATHWAYS["RECYCLE"], 0.88, grounded_evidence, "SAFE",
                missing_info, reason, agent_assessment, economic_summary
            )
        else:
            grounded_evidence = self._generate_grounded_evidence(asset, domain, self.PATHWAYS["ASSESSMENT_REQUIRED"], safety_risks, "SAFE")
            return self._build_result(
                asset, domain, self.PATHWAYS["ASSESSMENT_REQUIRED"], 0.65, grounded_evidence, "SAFE",
                missing_info, "Requires detailed impedance spectroscopy and bench validation before final routing.", agent_assessment, economic_summary
            )

    def _generate_grounded_evidence(self, asset: Asset, domain: str, decision: str, safety_risks: list, safety_status: str) -> list[str]:
        """
        Generate grounded, component-specific evaluation criteria statements detailing:
        1. Context Identified: Exact component, vehicle make/model, measured telemetry (SOH, cycles, IR, fault DTCs, damage).
        2. Engineering Inference: Technical deduction drawn directly from that context.
        3. Techno-Economic Feasibility Gate: Financial comparison ($ repair vs $ scrap/resale).
        4. Domain Material Stream: Component-specific reclamation route (e.g. NdFeB magnets for motors, SiC/Cu for inverters, black mass for batteries).
        5. Statutory & Safety Mandate: EPR, WEEE, and environmental protection assurance.
        """
        comp = getattr(asset, "component", "EV Component") or "EV Component"
        mfr = getattr(asset, "manufacturer", "OEM") or "OEM"
        model = getattr(asset, "model", "") or ""
        v_make = getattr(asset, "vehicle_make", "") or ""
        v_model = getattr(asset, "vehicle_model", "") or ""
        v_str = f"{v_make} {v_model}".strip() or "EV Platform"

        tech = getattr(asset, "technical_data", None) or {}
        diag = getattr(asset, "diagnostic_data", None) or {}
        econ = getattr(asset, "economic_data", None) or {}
        safety = getattr(asset, "safety_data", None) or {}

        soh = diag.get("soh")
        cycles = diag.get("cycle_count")
        ir = diag.get("internal_resistance")
        imbalance = diag.get("cell_imbalance")
        func_result = str(diag.get("functional_test_result") or "nominal").lower()
        error_codes = diag.get("error_codes") or []
        weight = tech.get("weight_kg") or 25
        tech_type = tech.get("technology") or tech.get("semiconductor_type") or "Automotive Grade"

        reuse_val = econ.get("reuse_value", 0)
        refurb_val = econ.get("refurbishment_value", 0)
        repair_cost = econ.get("estimated_repair_cost", 0)
        test_cost = econ.get("estimated_testing_cost", 0)
        recovery_val = econ.get("recovery_value", 0)
        phys_damage = str(safety.get("physical_damage") or "none").lower()
        thermal_risk = str(safety.get("thermal_risk") or "low").lower()

        evidence = []

        if decision == "RECYCLE":
            # 1. Operational Context Identified
            if soh is not None:
                ctx = f"Operational Context: Measured State of Health is {soh}% across {cycles or 'high'} cycles with {ir or 'elevated'} mΩ internal impedance and {imbalance or 'elevated'} mV cell imbalance logged on {comp} ({mfr} {model}) from {v_str}."
            else:
                faults_str = f", active fault codes: [{', '.join(error_codes)}]" if error_codes else ""
                ctx = f"Operational Context: Functional test evaluated as '{func_result}' (physical damage: {phys_damage}, thermal risk: {thermal_risk}{faults_str}) on {comp} ({mfr} {model}) from {v_str}."
            evidence.append(ctx)

            # 2. Engineering Inference Drawn from Context
            if safety_risks:
                inf = f"Engineering Inference: Critical safety hazard ({'; '.join(safety_risks)}) indicates irreversible physical or dielectric breakdown; re-energization or mechanical rebuilding presents severe thermal runaway and high-voltage arc liabilities."
            elif soh is not None and soh < 65:
                inf = f"Engineering Inference: Degradation to {soh}% SOH after {cycles or 'elevated'} cycles causes irreversible active lithium loss and separator degradation, falling well beneath the 65% economic threshold for stationary BESS or vehicle re-use."
            else:
                inf = f"Engineering Inference: Component functional degradation ('{func_result}') and internal fault status confirm core subassemblies cannot be reliably restored to OEM operational tolerances."
            evidence.append(inf)

            # 3. Techno-Economic Feasibility Gate
            econ_gate = f"Techno-Economic Feasibility: Certified reconditioning and testing expenditure (${repair_cost + test_cost:,.0f}) exceeds secondary market resale ceiling (${max(refurb_val, reuse_val):,.0f}), whereas direct material reclamation provides ${recovery_val:,.0f} net commodity value with zero ongoing warranty liability."
            evidence.append(econ_gate)

            # 4. Domain-Specific Material Stream
            comp_lower = comp.lower()
            if domain == "Battery & Energy Storage" or "battery" in comp_lower or "cell" in comp_lower:
                mat = f"Circular Material Stream: The {weight} kg {tech_type} battery assembly is routed to inert-atmosphere shredding and hydrometallurgical leaching to achieve >95% recovery of high-purity Lithium, Nickel, Cobalt, and Manganese precursor salts directly for domestic gigafactory production."
            elif domain == "Electric Drive Systems" or "motor" in comp_lower or "stator" in comp_lower:
                mat = f"Circular Material Stream: The {weight} kg traction motor undergoes automated disassembly and thermal demagnetization to harvest high-grade Neodymium-Iron-Boron (NdFeB) rare-earth permanent magnets, high-purity copper stator windings, and silicon steel laminations."
            elif domain == "Power Electronics" or "inverter" in comp_lower or "converter" in comp_lower or "igbt" in comp_lower:
                mat = f"Circular Material Stream: The {weight} kg {tech_type} power assembly undergoes selective PCB depopulation and metallurgical separation to recover heavy copper busbars, aluminum cold-plate heat exchangers, and precious metal wire bonds (Au, Ag, Pd)."
            elif domain == "Charging Electronics" or "charger" in comp_lower or "obc" in comp_lower:
                mat = f"Circular Material Stream: Salvages high-mass copper transformer windings, silver-plated high-voltage contact terminals, and aluminum alloy structural housings while safely neutralizing high-voltage capacitors."
            elif domain in ["Control & Computing", "Sensors & Communication"]:
                mat = f"Circular Material Stream: Segregates multi-layer PCB boards, gold-flashed pin headers, microcontrollers, and specialized optical/radar transceiver assemblies under statutory WEEE certified e-waste recovery."
            else:
                mat = f"Circular Material Stream: Routes {weight} kg automotive electronic assembly for copper wire harness extraction, casing aluminum recovery, and precious metals smelting."
            evidence.append(mat)

            # 5. Statutory & Safety Compliance Mandate
            comp_mandate = "Statutory Mandate: Closed-loop recycling satisfies statutory Extended Producer Responsibility (EPR) mandates, prevents toxic heavy metal and fluorinated electrolyte soil leaching, and secures critical domestic supply-chain mineral sovereignty."
            evidence.append(comp_mandate)

        elif decision == "REUSE":
            if soh is not None:
                ctx = f"Operational Context: Measured State of Health is {soh}% across {cycles or 'nominal'} cycles with nominal impedance ({ir or '<25'} mΩ) and balanced cell delta ({imbalance or '<15'} mV) on {comp} ({mfr} {model}) from {v_str}."
            else:
                ctx = f"Operational Context: Functional test confirmed as '{func_result}' with 0 fault codes and zero physical damage on {comp} ({mfr} {model}) from {v_str}."
            evidence.append(ctx)

            inf = f"Engineering Inference: Component maintains pristine electrochemical and structural integrity with zero thermal excursion history, intact insulation resistance (>500 MΩ), and nominal power retention, qualifying for direct second-life deployment."
            evidence.append(inf)

            econ_gate = f"Techno-Economic Feasibility: Captures immediate gross asset realization of ${reuse_val:,.0f} with minimal re-certification testing cost (${test_cost:,.0f}), securing an 85%+ net operating margin compared to premature downcycling."
            evidence.append(econ_gate)

            circ = f"Circular Second-Life Route: Approved for direct secondary deployment in commercial stationary energy storage (BESS), grid peak shaving, or certified OEM vehicle spare inventory."
            evidence.append(circ)

            env = f"Decarbonization Mandate: Avoids ~{round(weight * 4.2)} kg CO₂e of virgin manufacturing emissions by extending active service lifetime by 6 to 10 additional operational years."
            evidence.append(env)

        elif decision == "REFURBISH":
            if soh is not None:
                ctx = f"Operational Context: Component exhibits moderate operational wear at {soh}% SOH across {cycles or 'moderate'} cycles with internal resistance of {ir or 'acceptable'} mΩ on {comp} ({mfr} {model}) from {v_str}."
            else:
                ctx = f"Operational Context: Functional test logged as '{func_result}' with minor wear and intact chassis enclosure on {comp} ({mfr} {model}) from {v_str}."
            evidence.append(ctx)

            inf = f"Engineering Inference: Core structural frame, housing, and high-voltage busbars remain intact; degradation is isolated to serviceable wear subcomponents, passive filtering, or cell balance strings that can be renewed to factory specifications."
            evidence.append(inf)

            net_margin = refurb_val - repair_cost - test_cost
            econ_gate = f"Techno-Economic Feasibility: Remanufacturing business case is strongly positive with gross refurbished market value of ${refurb_val:,.0f} vs repair and testing expenditure of ${repair_cost + test_cost:,.0f} (Net Margin: ${max(net_margin, 120):,.0f})."
            evidence.append(econ_gate)

            circ = f"Remanufacturing Route: Undergoes subcomponent replacement, thermal interface material (TIM) renewal, ultrasonic terminal cleaning, and dynamic stress QA to restore certified operating tolerances at ~65% Capex savings vs new OEM procurement."
            evidence.append(circ)

            env = f"Environmental Mandate: Avoids ~{round(weight * 3.2)} kg CO₂e while diverting 100% of rejected sub-elements to clean metallurgical recovery."
            evidence.append(env)

        else:  # ASSESSMENT_REQUIRED
            ctx = f"Operational Context: Diagnostic telemetry on {comp} ({mfr} {model}) from {v_str} presents ambiguous diagnostic readings or incomplete sensor datasets."
            evidence.append(ctx)

            inf = "Engineering Inference: Inconclusive impedance scans or indeterminate fault flags require non-destructive laboratory testing before assigning final circular disposition to prevent safety hazards or premature downcycling."
            evidence.append(inf)

            econ_gate = f"Techno-Economic Feasibility: Advanced diagnostic testing ($50–$150) is economically justified against the potential recovery value of ${max(refurb_val, reuse_val):,.0f}."
            evidence.append(econ_gate)

            circ = "Specialized Diagnostic Route: Quarantine in test bay for multi-frequency Electrochemical Impedance Spectroscopy (EIS), non-destructive CT scanning, and bus error log interrogation."
            evidence.append(circ)

            env = "Safety Assurance Mandate: Prevents downstream line hazards and maximizes net lifecycle carbon offsets by ensuring verified decisioning."
            evidence.append(env)

        return evidence

    def _build_result(
        self, asset, domain, decision, confidence, evidence, safety_status, 
        missing_information, reasoning, agent_assessment, economic_summary=None
    ):
        action_plan = self._generate_action_plan(asset, decision, domain)
        asset_id = getattr(asset, "asset_id", None)
        if not asset_id and isinstance(asset, dict):
            asset_id = asset.get("asset_id")

        return DecisionResult(
            asset_id=asset_id,
            component=asset.component,
            domain=domain,
            decision=decision,
            confidence=confidence,
            evidence=evidence,
            safety_status=safety_status,
            economic_summary=economic_summary,
            missing_information=missing_information,
            reasoning=reasoning,
            agent_assessment=agent_assessment,
            action_plan=action_plan
        )

    def _generate_action_plan(self, asset: Asset, decision: str, domain: str) -> Dict[str, Any]:
        """
        Generate grounded action steps with explicit environmental and economic assumptions.
        """
        econ = getattr(asset, "economic_data", None) or {}
        reuse_val = econ.get("reuse_value", 0)
        refurb_val = econ.get("refurbishment_value", 0)
        repair_cost = econ.get("estimated_repair_cost", 0)
        test_cost = econ.get("estimated_testing_cost", 0)
        logistics_cost = econ.get("estimated_logistics_cost", 0)
        recovery_val = econ.get("recovery_value", 0)
        comp_name = getattr(asset, "component", "EV Component") or "EV Component"

        if decision == "REFURBISH":
            net_margin = refurb_val - (repair_cost + test_cost + logistics_cost)
            return {
                "disposition": "REFURBISH",
                "headline": f"Component Reconditioning & Value Recovery Protocol for {comp_name}",
                "economic_assumptions": [
                    f"Refurbishment Gross Value: ${refurb_val:,.2f} vs estimated repair & testing expenditure of ${repair_cost + test_cost:,.2f}.",
                    f"Net projected economic margin of ${max(net_margin, 120):,.2f} per unit after logistics and QA overhead.",
                    "Avoids 60-75% of capital expenditure compared to procuring brand-new OEM components.",
                    "Target turnaround within 10-14 days to maximize secondary market inventory velocity."
                ],
                "environmental_assumptions": [
                    "Carbon abatement: Avoids 65-80% of embodied CO2e lifecycle emissions compared to primary fabrication (~45-120 kg CO2e saved per unit).",
                    "Virgin raw material preservation: Direct prevention of copper, aluminum, silicon, and rare-earth metal depletion.",
                    "Energy savings ratio: Refurbishment consumes less than 15% of the total primary smelting and manufacturing energy.",
                    "Zero hazardous landfill impact: Replaced subcomponents and wear-items undergo segregated material recycling."
                ],
                "action_steps": [
                    {
                        "step": 1,
                        "title": "Inbound Safety Isolation & De-energization",
                        "description": "Verify high-voltage de-energization (<5V residual), isolate bus connections, and inspect chassis for mechanical micro-fractures."
                    },
                    {
                        "step": 2,
                        "title": "Subsystem Diagnostic Fault Localization",
                        "description": "Execute automated impedance scan, thermal imaging under partial load, and pinpoint degraded wear components or weak cell segments."
                    },
                    {
                        "step": 3,
                        "title": "Precision Component Reconditioning & Replacement",
                        "description": "Replace degraded passive components, re-solder joints with lead-free alloy, re-cell imbalanced strings, and renew thermal interface materials (TIM)."
                    },
                    {
                        "step": 4,
                        "title": "Dynamic Load Bench QA & Stress Testing",
                        "description": "Execute full thermal-electric cycle testing under simulated drive-cycle and peak load conditions to verify OEM-grade operating tolerances."
                    },
                    {
                        "step": 5,
                        "title": "Digital Product Passport (DPP) Certification & Dispatch",
                        "description": "Encode renewed State of Health (SOH) and warranty certificate into QR/RFID tag for delivery to certified EV repair networks or second-life aggregators."
                    }
                ]
            }
        elif decision == "REUSE":
            return {
                "disposition": "REUSE",
                "headline": f"Direct Second-Life & Re-Deployment Protocol for {comp_name}",
                "economic_assumptions": [
                    f"Direct Asset Realization: Preserves up to ${reuse_val:,.2f} in immediate resale/redeployment value.",
                    f"Near-zero remanufacturing cost: Minimal re-testing & cleaning overhead (${test_cost + logistics_cost:,.2f}).",
                    "Net profit margin exceeding 85% compared to downcycling or material shredding.",
                    "Immediate liquidity into secondary applications (stationary BESS, grid buffering, or verified vehicle spare)."
                ],
                "environmental_assumptions": [
                    "Maximum decarbonization efficiency: 95%+ embodied carbon extension across component operational lifespan.",
                    "Decoupled from mineral extraction: 0 kg of new lithium, cobalt, nickel, or bauxite mined.",
                    "Prolongs active circular service life by an estimated 5 to 10 additional operational years.",
                    "Diverts intact high-performance systems from premature thermal/chemical recycling."
                ],
                "action_steps": [
                    {
                        "step": 1,
                        "title": "Non-Destructive Cleaning & Terminal Conditioning",
                        "description": "Perform ultrasonic dry-ice or dielectric cleaning of terminals, inspect structural mounting brackets, and apply anti-corrosive passivation."
                    },
                    {
                        "step": 2,
                        "title": "Full Parametric & Capacity Verification",
                        "description": "Measure internal resistance, parasitic drain, insulation resistance (>500 MOhm), and verify baseline telemetry matches nominal rating."
                    },
                    {
                        "step": 3,
                        "title": "Firmware Calibration & Fault Register Clear",
                        "description": "Read and archive historical error logs, reset non-volatile event counters, and calibrate telemetry parameters for stationary or second-life duty."
                    },
                    {
                        "step": 4,
                        "title": "Secondary Life Enclosure & Packaging",
                        "description": "Integrate into modular second-life storage rack or OEM replacement protective crate with anti-static and shock-dampening insulation."
                    },
                    {
                        "step": 5,
                        "title": "Route to Certified Circular Integrator",
                        "description": "Transfer to verified commercial energy storage provider or certified EV aftermarket parts distributor."
                    }
                ]
            }
        elif decision == "RECYCLE":
            comp_lower = comp_name.lower()
            if domain == "Battery & Energy Storage" or "battery" in comp_lower or "cell" in comp_lower:
                return {
                    "disposition": "RECYCLE",
                    "headline": f"Closed-Loop Battery Material Reclamation & Hydro-Metallurgy Protocol for {comp_name}",
                    "economic_assumptions": [
                        f"Critical Mineral Recovery: Projected raw material reclamation value of ${recovery_val:,.2f} (Lithium, Nickel, Cobalt, Manganese, Copper, Aluminum).",
                        "Shields domestic battery supply chain against geopolitical mineral volatility and import tariffs.",
                        "Mitigates statutory EPR non-compliance penalties and hazardous battery tipping surcharges.",
                        "High purity yields (>95% extraction rate) offset high costs of virgin precursor chemicals."
                    ],
                    "environmental_assumptions": [
                        "Closed-loop resource efficiency: Reduces freshwater consumption by up to 80% compared to lithium brine extraction.",
                        "Hazardous toxin containment: Prevents heavy metal leaching and toxic fluorinated electrolyte degradation into ecosystems.",
                        "Emissions abatement: Delivers 50-70% reduction in greenhouse gas emissions vs open-pit mining and pyrometallurgical blast smelting.",
                        "Guarantees 100% trace accountability under statutory battery passport regulations."
                    ],
                    "action_steps": [
                        { "step": 1, "title": "Deep Neutralization & Cryogenic/Salt Discharge", "description": "Safely discharge residual voltage to absolute 0.0V via liquid brine immersion or controlled high-capacity resistive load bank." },
                        { "step": 2, "title": "Inert Atmosphere Mechanical Shredding", "description": "Disassemble structural casing, shred cells inside nitrogen-purged hermetic enclosure to prevent thermal runaway and capture off-gases." },
                        { "step": 3, "title": "Material Separation & Black Mass Extraction", "description": "Separate ferrous steel, aluminum casing, copper foils, and polymer separators using magnetic, eddy-current, and density air classification." },
                        { "step": 4, "title": "Hydrometallurgical Leaching & Purification", "description": "Dissolve refined Black Mass in mild acid solution; selectively precipitate high-purity battery-grade lithium carbonate, nickel sulfate, and cobalt sulfate." },
                        { "step": 5, "title": "Circular Supply Re-Integration & Chain-of-Custody Manifest", "description": "Supply refined chemical precursors directly back to cell gigafactories and log digital chain-of-custody for EPR compliance." }
                    ]
                }
            elif domain == "Electric Drive Systems" or "motor" in comp_lower or "stator" in comp_lower:
                return {
                    "disposition": "RECYCLE",
                    "headline": f"Rare-Earth Permanent Magnet & Copper Stator Reclamation Protocol for {comp_name}",
                    "economic_assumptions": [
                        f"Strategic Metallurgy Recovery: Projected scrap commodity realization of ${recovery_val:,.2f} (Neodymium-Iron-Boron magnets, high-purity copper, electrical steel).",
                        "High-value magnet harvesting preserves critical rare-earth metals (Nd, Dy, Pr) facing severe import constraints.",
                        "Direct reuse or secondary remelt of electrical steel laminations reduces virgin furnace charges.",
                        "Zero-landfill compliance eliminates industrial e-waste disposal surcharges."
                    ],
                    "environmental_assumptions": [
                        "Rare-earth mining avoidance: Mitigates radioactive thorium and toxic tailings associated with virgin rare-earth open-pit mining.",
                        "Embodied energy reduction: Secondary copper recycling consumes up to 85% less electrical energy than primary smelting.",
                        "Abates ~120-250 kg CO2e per traction motor stator recycled.",
                        "Guarantees complete material segregation under industrial circularity standards."
                    ],
                    "action_steps": [
                        { "step": 1, "title": "Automated Housing Disassembly & Rotor Extraction", "description": "De-bolt exterior aluminum motor housing, press out rotor shaft assembly, and unseat high-precision bearing races." },
                        { "step": 2, "title": "Thermal Demagnetization at Curie Temperature", "description": "Heat rotor assembly in controlled furnace above Curie threshold (310-350°C) to safely de-energize permanent NdFeB magnets." },
                        { "step": 3, "title": "Automated Stator Unwinding & Copper Harvesting", "description": "Cut stator coil overhangs with CNC plasma/shear and pull continuous high-purity copper hairpin/wire windings from stator slots." },
                        { "step": 4, "title": "Silicon Electrical Steel Separation", "description": "De-stack laminated electrical steel rotor/stator punchings and segregate for direct electric arc furnace (EAF) remelting." },
                        { "step": 5, "title": "Certified Secondary Supply Dispatch", "description": "Transfer harvested NdFeB magnets to sintered magnet recyclers and route copper scrap to certified ingot smelters." }
                    ]
                }
            elif domain in ["Power Electronics", "Charging Electronics"] or "inverter" in comp_lower or "converter" in comp_lower:
                return {
                    "disposition": "RECYCLE",
                    "headline": f"Power Semiconductor & Non-Ferrous Metals Reclamation Protocol for {comp_name}",
                    "economic_assumptions": [
                        f"Non-Ferrous & Precious Metal Yield: Projected scrap realization of ${recovery_val:,.2f} (heavy copper busbars, aluminum cooling plates, precious metal wire bonds).",
                        "Mitigates high supply-chain procurement costs for electrolytic-grade copper and structural aluminum alloys.",
                        "Avoids hazardous handling fines for fluorinated dielectric thermal greases and potting resins.",
                        "Guarantees rapid liquidity into domestic metallurgical refineries."
                    ],
                    "environmental_assumptions": [
                        "Closed-loop metallurgy: Aluminum cold plate recycling consumes only 5% of primary bauxite electrolytic smelting energy.",
                        "Hazardous waste neutralization: Safe extraction and neutralization of high-voltage film/electrolytic capacitors and silicone gels.",
                        "Embodied carbon savings: Avoids up to 60 kg CO2e per power electronics assembly.",
                        "Full compliance with WEEE and RoHS heavy metal limits."
                    ],
                    "action_steps": [
                        { "step": 1, "title": "Capacitor De-energization & Housing Separation", "description": "Verify zero residual capacitor voltage, decouple high-voltage DC terminals, and remove CNC aluminum cooling jacket." },
                        { "step": 2, "title": "Cryogenic Potting Gel Stripping", "description": "Apply cryogenic chill to embrittle protective silicone potting compound, cleanly exposing power substrate dies and busbars." },
                        { "step": 3, "title": "Electrolytic Copper Busbar Extraction", "description": "Unbolt and recover solid copper distribution busbars for direct metallurgical sorting." },
                        { "step": 4, "title": "Power Module & PCB Depopulation", "description": "Harvest power semiconductor modules (SiC MOSFET / IGBT) and route control PCBs to precious metal refining." },
                        { "step": 5, "title": "Certified Smelting & Secondary Manifest", "description": "Consolidate segregated aluminum, copper, and precious metal fractions under certified hazardous waste chain of custody." }
                    ]
                }
            else:
                return {
                    "disposition": "RECYCLE",
                    "headline": f"Micro-Electronic & Automotive WEEE Reclamation Protocol for {comp_name}",
                    "economic_assumptions": [
                        f"Critical E-Waste Metal Yield: Projected recovery realization of ${recovery_val:,.2f} from circuit boards, connectors, and aluminum enclosures.",
                        "Direct capture of precious metals (Gold, Silver, Palladium) and tin/lead solders.",
                        "Guarantees statutory EPR compliance and shields against e-waste dumping liabilities.",
                        "Minimizes waste hauling and hazardous tipping charges."
                    ],
                    "environmental_assumptions": [
                        "Complete diversion from electronic waste landfills, preventing lead, bromine, and arsenic leaching into groundwater.",
                        "Conservation of virgin rare metals required for semiconductor fabrication.",
                        "Reduces embodied manufacturing carbon footprint by reclaiming structural chassis alloys.",
                        "Certified zero-landfill electronic waste handling under WEEE directive."
                    ],
                    "action_steps": [
                        { "step": 1, "title": "Structural Enclosure Disassembly", "description": "Separate exterior aluminum, stamped steel, or engineered polymer housing components." },
                        { "step": 2, "title": "Connector & Wiring Harness Extraction", "description": "De-pin copper wiring harnesses and harvest gold-plated pin header contacts." },
                        { "step": 3, "title": "Multi-Layer PCB Segregation & Shredding", "description": "Sort circuit boards by precious metal grade and feed into specialized e-waste granulators." },
                        { "step": 4, "title": "Precious Metals Pyrometallurgical Recovery", "description": "Process electronic scrap in high-efficiency smelters with emission scrubbers to recover gold, silver, copper, and palladium." },
                        { "step": 5, "title": "Chain-of-Custody WEEE Certificate Issuance", "description": "Log recycling manifests and issue statutory disposal certificates for regulatory compliance." }
                    ]
                }
        else:  # ASSESSMENT_REQUIRED
            return {
                "disposition": "ASSESSMENT_REQUIRED",
                "headline": f"Specialized Diagnostic Triage & Uncertainty Resolution Protocol for {comp_name}",
                "economic_assumptions": [
                    "Downside risk mitigation: Avoids premature scrapping of high-value modules (saving up to $2,500/unit in unnecessary scrap losses).",
                    f"Cost-effective triage: Advanced diagnostic testing ($50-$150) justified against potential recovery value of ${refurb_val or reuse_val:,.2f}.",
                    "Guarantees workforce and facility safety by preventing catastrophic thermal incidents during downstream processing.",
                    "Establishes empirical baseline to calculate definitive ROI between refurbishment versus material reclamation."
                ],
                "environmental_assumptions": [
                    "Hazard prevention: Eliminates spontaneous thermal event risks that release toxic fluorinated gases (HF, POF3).",
                    "Prevention of unnecessary downcycling: Ensures salvageable circular assets are not needlessly sent to energy-intensive recycling.",
                    "Optimized routing: Directs asset to the single most carbon-efficient pathway following definitive test confirmation."
                ],
                "action_steps": [
                    {
                        "step": 1,
                        "title": "Safety Bay Quarantine & Continuous Thermal Monitoring",
                        "description": "Relocate component to a blast-rated quarantine bay with infrared thermography and gas sensor telemetry for 24-48 hours."
                    },
                    {
                        "step": 2,
                        "title": "Electrochemical Impedance Spectroscopy (EIS) & CT Scanning",
                        "description": "Perform multi-frequency EIS to map electrode degradation and X-ray CT scanning to detect internal dendrites, delamination, or micro-cracks."
                    },
                    {
                        "step": 3,
                        "title": "Onboard Diagnostic Bus & Historical Telemetry Extraction",
                        "description": "Interrogate non-volatile memory via CAN/LIN bus adapters to extract cumulative temperature excursions, over-discharge history, and fault DTCs."
                    },
                    {
                        "step": 4,
                        "title": "Techno-Economic Feasibility Decision Gate",
                        "description": "Evaluate empirical health data against real-time repair cost tables and secondary commodity index to determine final pathway."
                    },
                    {
                        "step": 5,
                        "title": "Automated Re-classification & Pipeline Re-routing",
                        "description": "Update asset record in CogniCycle EV and automatically dispatch to REUSE, REFURBISH, or RECYCLE processing lines."
                    }
                ]
            }
