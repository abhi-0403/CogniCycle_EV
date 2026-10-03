import React, { useState, useEffect, useMemo, useCallback } from "react";
import Navbar from "../navigation/Navbar";
import OverviewView from "../views/OverviewView";
import TriageExplorerView from "../views/TriageExplorerView";
import UploadView from "../views/UploadView";
import ActionPlansView from "../views/ActionPlansView";
import AnalyticsView from "../views/AnalyticsView";
import ActionPlanModal from "../modals/ActionPlanModal";
import AssetDetailModal from "../modals/AssetDetailModal";
import DispositionRationaleModal from "../modals/DispositionRationaleModal";
import "./Dashboard.css";

// Dynamic domain heuristic fallback for instant offline/concurrency recovery
function getTailoredFallbackPlan(item) {
  const comp = item.component || "EV Component";
  const dec = item.decision || "REUSE";
  const raw = item.raw_asset || {};
  const mfr = raw.manufacturer || "OEM";
  const model = raw.model || "";
  const vehicle = `${raw.vehicle_make || ""} ${raw.vehicle_model || ""}`.trim() || "EV Vehicle";
  const tech = raw.technical_data || {};
  const diag = raw.diagnostic_data || {};
  const econ = raw.economic_data || {};
  const soh = diag.soh ?? 80;
  const cycles = diag.cycle_count || 450;
  const weight = tech.weight_kg || 25;
  const refurbVal = econ.refurbishment_value || 1400;
  const repairCost = econ.estimated_repair_cost || 180;
  const testCost = econ.estimated_testing_cost || 90;
  const logisticsCost = econ.estimated_logistics_cost || 50;
  const reuseVal = econ.reuse_value || 1900;
  const recoveryVal = econ.recovery_value || 280;

  if (dec === "REFURBISH") {
    return {
      disposition: "REFURBISH",
      headline: `Refurbishment & Precision Re-manufacturing Protocol for ${mfr} ${model} (${comp})`,
      economic_assumptions: [
        `Gross Refurbished Market Value: $${refurbVal.toLocaleString()} vs total repair & test budget of $${(repairCost + testCost).toLocaleString()}.`,
        `Net operational margin: $${(refurbVal - repairCost - testCost - logisticsCost).toLocaleString()} per unit after reverse logistics.`,
        `Provides ~65% Capex savings for ${vehicle} fleet operators compared to new OEM replacements.`
      ],
      environmental_assumptions: [
        `Avoids ~${Math.max(Math.round(weight * 3.8), 65)} kg of embodied CO2e emissions compared to virgin primary production.`,
        `Conserves strategic copper, structural aluminum, and ${tech.technology || "active battery materials"}.`,
        `Smelting energy abatement: Consumes less than 15% of the energy of virgin fabrication.`
      ],
      action_steps: [
        { step: 1, title: `High-Voltage Isolation & Diagnostic Scanning for ${comp}`, description: `De-energize terminals on ${mfr} ${model}, confirm zero residual voltage (<5V), and scan CAN bus diagnostic logs.` },
        { step: 2, title: "Subsystem Telemetry Impedance & Thermal Localization", description: `Perform precision micro-ohmmeter tests to locate degraded cells or MOSFETs (baseline SOH: ${soh}%, cycles: ${cycles}).` },
        { step: 3, title: "Precision Component Renewal & Contact Re-flow", description: "Replace degraded sub-elements, re-apply high-conductivity thermal paste, and clean high-current busbars." },
        { step: 4, title: `Full-Duty Load Profiling matching ${vehicle} Parameters`, description: "Subject reconditioned assembly to simulated dynamic charge/discharge profiles and monitor thermals." },
        { step: 5, title: "Digital Product Passport (DPP) Certification & Dispatch", description: "Issue calibrated health rating, log barcode into CogniCycle EV database, and dispatch to warranty distributor." }
      ],
      is_cached: true
    };
  } else if (dec === "REUSE") {
    return {
      disposition: "REUSE",
      headline: `Direct Second-Life & Energy Storage Deployment Protocol for ${mfr} ${model} (${comp})`,
      economic_assumptions: [
        `Direct Asset Realization: Preserves up to $${reuseVal.toLocaleString()} in immediate resale value.`,
        `Minimal processing capex: Limited to terminal cleaning, bench testing, and re-packaging (<$${testCost + logisticsCost}).`,
        `High operating margin exceeding 85% with immediate liquidity into secondary storage channels.`
      ],
      environmental_assumptions: [
        `Maximum decarbonization: 95%+ embodied carbon extension for this ${mfr} ${model} (${weight} kg).`,
        `Zero virgin mining: Eliminates mineral extraction demand for an equivalent replacement unit.`,
        `Extends circular service lifetime by an estimated 6 to 10 additional operational years.`
      ],
      action_steps: [
        { step: 1, title: "Precision Terminal Cleaning & Decontamination", description: `Perform ultrasonic dry-ice cleaning on bus terminals of ${mfr} ${model} and inspect mounting points.` },
        { step: 2, title: "Insulation & High-Potential Safety Testing", description: `Verify insulation resistance exceeds 500 MOhm at 1000V DC (verified SOH: ${soh}%).` },
        { step: 3, title: "Firmware Re-Calibration & History Archiving", description: "Archive past vehicle telemetry, clear transient fault codes, and configure BMS for stationary storage mode." },
        { step: 4, title: "Modular Enclosure Packaging", description: "Mount into standardized modular protective rack with shock isolation and thermal barrier." },
        { step: 5, title: "Dispatch to Certified Stationary Storage Integrator", description: "Deliver component to certified commercial solar energy storage facility or verified EV aftermarket distributor." }
      ],
      is_cached: true
    };
  } else if (dec === "RECYCLE") {
    return {
      disposition: "RECYCLE",
      headline: `Closed-Loop Material Reclamation & Hydrometallurgy Protocol for ${mfr} ${model} (${comp})`,
      economic_assumptions: [
        `Raw Material Reclamation: Projected mineral recovery value of $${recoveryVal.toLocaleString()} (${tech.technology || "battery/electronic metals"}).`,
        `Shields domestic supply chain against international price volatility and virgin commodity tariffs.`,
        `Avoids strict regulatory EPR non-compliance fines and hazardous waste tipping surcharges.`
      ],
      environmental_assumptions: [
        `Water & resource conservation: Uses up to 80% less freshwater compared to primary ore mining.`,
        `Hazard containment: Safely neutralizes toxic electrolytes and heavy metals associated with ${comp}.`,
        `Emissions mitigation: 50-70% lower greenhouse gas footprint compared to virgin open-pit mining.`
      ],
      action_steps: [
        { step: 1, title: "Deep Neutralization & Cryogenic/Salt Discharge", description: `Safely discharge residual voltage of ${mfr} ${model} to 0.0V via salt-bath immersion or resistive sink.` },
        { step: 2, title: "Inert-Gas Atmosphere Shredding", description: `Dismantle chassis of ${comp}; shred interior elements under a nitrogen blanket to prevent thermal runaway.` },
        { step: 3, title: "Multi-Stage Density & Magnetic Classification", description: "Separate ferrous structural steel, aluminum casings, copper foils, and polymer separators." },
        { step: 4, title: "Hydrometallurgical Acid Leaching & Purification", description: "Dissolve concentrated Black Mass; selectively precipitate battery-grade lithium carbonate, nickel, and cobalt sulfates." },
        { step: 5, title: "Circular Supply Re-Integration Manifest", description: "Log certified chemical assay data and dispatch reclaimed precursors directly to domestic battery gigafactories." }
      ],
      is_cached: true
    };
  } else {
    return {
      disposition: "ASSESSMENT_REQUIRED",
      headline: `Specialized Diagnostic Triage & Quarantine Protocol for ${mfr} ${model} (${comp})`,
      economic_assumptions: [
        `Downside risk mitigation: Prevents premature scrapping of salvageable assembly (potential value: $${refurbVal.toLocaleString()}).`,
        `Cost-effective triage: Advanced diagnostic testing ($${testCost}) justified against high recovery valuation.`,
        `Workforce safety assurance: Eliminates catastrophic fire or shock hazards on downstream handling lines.`
      ],
      environmental_assumptions: [
        `Toxic event prevention: Eliminates spontaneous thermal runaway that emits hazardous gases.`,
        `Prevention of downcycling: Guarantees salvageable assemblies are not needlessly smelted.`,
        `Optimized lifecycle routing: Selects highest net carbon-offset disposition post-test.`
      ],
      action_steps: [
        { step: 1, title: "Safety Quarantine & Infrared Monitoring", description: `Quarantine ${mfr} ${model} in fire-rated bay with continuous thermal camera and gas monitoring for 24 hours.` },
        { step: 2, title: "Electrochemical Impedance & CT Inspection", description: "Conduct multi-frequency EIS analysis and industrial X-ray tomography to inspect internal structural integrity." },
        { step: 3, title: "Telemetry & Non-Volatile Memory Extraction", description: "Interrogate CAN bus memory to review lifetime peak temperatures, over-voltage events, and cycle history." },
        { step: 4, title: "Techno-Economic Triage Decision Gate", description: "Compare verified health parameters against current repair cost thresholds to finalize pathway." },
        { step: 5, title: "Re-classification & Automated Routing", description: "Update CogniCycle EV database with final assessment and release component to designated workflow." }
      ],
      is_cached: true
    };
  }
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [stats, setStats] = useState({
    total: 0,
    reuse: 0,
    refurbish: 0,
    recycle: 0,
    assessmentRequired: 0
  });
  const [decisions, setDecisions] = useState([]);
  const [datasetSource, setDatasetSource] = useState("cache");
  const [isLoading, setIsLoading] = useState(false);

  // Persistent Action Plans cache
  const [savedPlans, setSavedPlans] = useState({});

  // Modals state
  const [selectedActionItem, setSelectedActionItem] = useState(null);
  const [activePlan, setActivePlan] = useState(null);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);

  const [selectedInspectItem, setSelectedInspectItem] = useState(null);
  const [isInspectModalOpen, setIsInspectModalOpen] = useState(false);

  // Interactive Lighten Rationale Modal state
  const [selectedRationaleItem, setSelectedRationaleItem] = useState(null);
  const [isRationaleModalOpen, setIsRationaleModalOpen] = useState(false);

  // Calculate statistics from decision list
  const computeStats = (items) => {
    let s = { total: items.length, reuse: 0, refurbish: 0, recycle: 0, assessmentRequired: 0 };
    for (const item of items) {
      if (item.decision === "REUSE") s.reuse++;
      else if (item.decision === "REFURBISH") s.refurbish++;
      else if (item.decision === "RECYCLE") s.recycle++;
      else if (item.decision === "ASSESSMENT_REQUIRED") s.assessmentRequired++;
    }
    return s;
  };

  // Main data fetcher: Single call to /assets/triage
  const loadTriageData = useCallback(async (forceRerun = false) => {
    try {
      setIsLoading(true);
      const url = forceRerun
        ? "http://localhost:8000/assets/triage/rerun"
        : "http://localhost:8000/assets/triage";
      const method = forceRerun ? "POST" : "GET";

      const res = await fetch(url, { method });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();

      const items = json.data || [];
      setDecisions(items);
      setStats(computeStats(items));
      setDatasetSource(json.source || (forceRerun ? "fresh" : "cache"));

      // Load existing saved action plans
      try {
        const plansRes = await fetch("http://localhost:8000/assets/action-plans");
        if (plansRes.ok) {
          const plansData = await plansRes.json();
          if (plansData && typeof plansData === "object") {
            setSavedPlans(plansData);
          }
        }
      } catch (err) {
        console.warn("Could not load saved action plans:", err);
      }
    } catch (err) {
      console.error("Failed to load triage data:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch on mount (SINGLE call)
  useEffect(() => {
    loadTriageData(false);
  }, [loadTriageData]);

  // ON-DEMAND ACTION PLAN GENERATION
  const handleTakeAction = async (item, forceRegenerate = false) => {
    setSelectedActionItem(item);
    setIsActionModalOpen(true);

    const assetId = item.asset_id;

    // Check frontend cache first if not forcing regeneration
    if (!forceRegenerate && savedPlans[assetId]) {
      setActivePlan({ ...savedPlans[assetId], is_cached: true });
      setIsGeneratingPlan(false);
      return;
    }

    setIsGeneratingPlan(true);
    setActivePlan(null);

    try {
      const response = await fetch("http://localhost:8000/assets/action-plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          asset: item.raw_asset || {
            asset_id: item.asset_id,
            component: item.component,
            domain: item.domain,
            condition: item.safety_status
          },
          decision: item.decision,
          confidence: item.confidence,
          safety_status: item.safety_status,
          reasoning: item.reasoning,
          force_regenerate: forceRegenerate
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const planResult = await response.json();
      setActivePlan(planResult);

      if (assetId) {
        setSavedPlans((prev) => ({
          ...prev,
          [assetId]: planResult
        }));
      }
    } catch (err) {
      console.warn("Generating grounded engineering protocol fallback:", err);
      const fallback = item.action_plan || getTailoredFallbackPlan(item);
      setActivePlan(fallback);
      if (assetId) {
        setSavedPlans((prev) => ({
          ...prev,
          [assetId]: fallback
        }));
      }
    } finally {
      setIsGeneratingPlan(false);
    }
  };

  const handleInspectItem = (item) => {
    setSelectedInspectItem(item);
    setIsInspectModalOpen(true);
  };

  const handleOpenRationale = (item) => {
    setSelectedRationaleItem(item);
    setIsRationaleModalOpen(true);
  };

  const handleDatasetUploaded = (newAnalyzedAssets, source = "uploaded") => {
    setDecisions(newAnalyzedAssets);
    setStats(computeStats(newAnalyzedAssets));
    setDatasetSource(source);
    setActiveTab("triage");
  };

  const handleOpenPlanFromArchive = (item, plan) => {
    setSelectedActionItem(item);
    setActivePlan({ ...plan, is_cached: true });
    setIsActionModalOpen(true);
  };

  return (
    <div className="cognicycle-app">
      {/* Top Sticky Modern Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        stats={stats}
        datasetSource={datasetSource}
        datasetCount={decisions.length}
        isLoading={isLoading}
        onRefresh={() => loadTriageData(true)}
        savedPlansCount={Object.keys(savedPlans).length}
      />

      {/* Main Active View */}
      <main className="main-content-area">
        {activeTab === "overview" && (
          <OverviewView
            stats={stats}
            datasetCount={decisions.length}
            datasetSource={datasetSource}
            recentDecisions={decisions}
            onNavigateTab={setActiveTab}
            onTakeAction={handleTakeAction}
            onInspectItem={handleInspectItem}
            onOpenRationale={handleOpenRationale}
          />
        )}

        {activeTab === "triage" && (
          <TriageExplorerView
            decisions={decisions}
            savedPlans={savedPlans}
            onTakeAction={handleTakeAction}
            onInspectItem={handleInspectItem}
            onOpenRationale={handleOpenRationale}
          />
        )}

        {activeTab === "upload" && (
          <UploadView
            onDatasetUploaded={handleDatasetUploaded}
            onSwitchToExplorer={() => setActiveTab("triage")}
          />
        )}

        {activeTab === "action_plans" && (
          <ActionPlansView
            savedPlans={savedPlans}
            allDecisions={decisions}
            onOpenPlan={handleOpenPlanFromArchive}
            onNavigateToExplorer={() => setActiveTab("triage")}
          />
        )}

        {activeTab === "analytics" && (
          <AnalyticsView decisions={decisions} stats={stats} />
        )}
      </main>

      {/* Interactive Lighten Disposition Rationale Modal */}
      <DispositionRationaleModal
        isOpen={isRationaleModalOpen}
        onClose={() => setIsRationaleModalOpen(false)}
        item={selectedRationaleItem}
        onTakeAction={handleTakeAction}
      />

      {/* Action Plan Standard Operating Procedure Modal */}
      <ActionPlanModal
        isOpen={isActionModalOpen}
        onClose={() => setIsActionModalOpen(false)}
        item={selectedActionItem}
        plan={activePlan}
        isGenerating={isGeneratingPlan}
        onRegenerate={(item) => handleTakeAction(item, true)}
      />

      {/* Asset Detail Telemetry Modal */}
      <AssetDetailModal
        isOpen={isInspectModalOpen}
        onClose={() => setIsInspectModalOpen(false)}
        item={selectedInspectItem}
        onTakeAction={handleTakeAction}
      />
    </div>
  );
}