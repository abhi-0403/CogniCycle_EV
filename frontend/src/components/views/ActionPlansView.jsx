import React, { useState } from "react";
import {
  FileCheck2,
  Sparkles,
  Download,
  Filter,
  ArrowRight,
  DollarSign,
  Leaf,
  Layers,
  CheckCircle2,
  ShieldCheck
} from "lucide-react";
import "./ActionPlansView.css";

export default function ActionPlansView({
  savedPlans = {},
  allDecisions = [],
  onOpenPlan,
  onNavigateToExplorer
}) {
  const [filter, setFilter] = useState("ALL");

  // Format plans list with matching decision info if available
  const planList = Object.entries(savedPlans).map(([assetId, plan]) => {
    const match = allDecisions.find((d) => d.asset_id === assetId);
    return {
      asset_id: assetId,
      component: match?.component || "EV Component",
      domain: match?.domain || "E-Drive",
      decision: plan.disposition || match?.decision || "REUSE",
      raw_asset: match?.raw_asset || {},
      confidence: match?.confidence || 0.9,
      safety_status: match?.safety_status || "SAFE",
      plan
    };
  });

  const filteredPlans = filter === "ALL"
    ? planList
    : planList.filter((p) => p.decision === filter);

  // Compute aggregate stats
  const totalSaved = planList.length;
  const reuseCount = planList.filter((p) => p.decision === "REUSE").length;
  const refurbishCount = planList.filter((p) => p.decision === "REFURBISH").length;
  const recycleCount = planList.filter((p) => p.decision === "RECYCLE").length;

  const handleExportJson = () => {
    const jsonStr = JSON.stringify(savedPlans, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cognicycle_action_plans_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="plans-view-container">
      {/* Header */}
      <div className="plans-header">
        <div>
          <div className="plans-tagline">
            <ShieldCheck size={14} className="tag-icon" />
            <span>AUDITED ACTION PROTOCOLS ARCHIVE</span>
          </div>
          <h2>Grounded Circular Operating Protocols</h2>
          <p>
            Central registry of verified circular operating procedures, techno-economic valuations, and decarbonization manifests across all 7 EV component pillars.
          </p>
        </div>

        {totalSaved > 0 && (
          <button className="export-json-btn" onClick={handleExportJson}>
            <Download size={15} />
            <span>Export Action Plans JSON</span>
          </button>
        )}
      </div>

      {/* Metric Cards */}
      <div className="plans-metrics-grid">
        <div className="plan-metric-card">
          <span className="p-metric-label">Certified Protocols</span>
          <span className="p-metric-val">{totalSaved}</span>
          <span className="p-metric-sub">Standard operating procedures</span>
        </div>
        <div className="plan-metric-card">
          <span className="p-metric-label">Reuse Pathways</span>
          <span className="p-metric-val val-green">{reuseCount}</span>
          <span className="p-metric-sub">Direct 2nd life deployments</span>
        </div>
        <div className="plan-metric-card">
          <span className="p-metric-label">Refurbish Protocols</span>
          <span className="p-metric-val val-blue">{refurbishCount}</span>
          <span className="p-metric-sub">Remanufacturing procedures</span>
        </div>
        <div className="plan-metric-card">
          <span className="p-metric-label">Recycling Precursors</span>
          <span className="p-metric-val val-amber">{recycleCount}</span>
          <span className="p-metric-sub">Hydrometallurgy extraction</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="plans-filter-bar">
        <div className="filter-buttons">
          {["ALL", "REUSE", "REFURBISH", "RECYCLE", "ASSESSMENT_REQUIRED"].map((f) => (
            <button
              key={f}
              className={`filter-btn ${filter === f ? "active" : ""}`}
              onClick={() => setFilter(f)}
            >
              {f.replace("_", " ")}
            </button>
          ))}
        </div>
        <span className="plans-count-badge">
          Showing {filteredPlans.length} of {totalSaved} Protocols
        </span>
      </div>

      {/* Plans List or Empty State */}
      {filteredPlans.length === 0 ? (
        <div className="plans-empty-card">
          <div className="empty-icon-circle">
            <FileCheck2 size={32} />
          </div>
          <h3>
            {totalSaved === 0
              ? "No Action Protocols Generated Yet"
              : `No ${filter} Protocols Saved`}
          </h3>
          <p>
            {totalSaved === 0
              ? "Select any component in the Triage Explorer and click 'Take Action' to synthesize grounded engineering action protocols."
              : "Try switching to 'ALL' to view existing protocols."}
          </p>
          {totalSaved === 0 && (
            <button className="goto-explorer-btn" onClick={onNavigateToExplorer}>
              <span>Go to Triage Explorer</span>
              <ArrowRight size={15} />
            </button>
          )}
        </div>
      ) : (
        <div className="plans-grid">
          {filteredPlans.map((item) => (
            <div key={item.asset_id} className="plan-archive-card">
              <div className="card-top-row">
                <div className="card-id-block">
                  <span className="archive-asset-id">{item.asset_id}</span>
                  <strong className="archive-comp-title">{item.component}</strong>
                </div>
                <div className="card-top-right">
                  <span className={`disposition-tag ${item.decision?.toLowerCase()}`}>
                    {item.decision}
                  </span>
                  <span className="cached-disk-badge" title="Verified protocol">
                    <ShieldCheck size={11} /> Audited
                  </span>
                </div>
              </div>

              <p className="archive-headline">{item.plan.headline}</p>

              <div className="archive-assumptions-preview">
                {item.plan.economic_assumptions?.[0] && (
                  <div className="preview-line">
                    <DollarSign size={13} className="prev-icon econ" />
                    <span>{item.plan.economic_assumptions[0]}</span>
                  </div>
                )}
                {item.plan.environmental_assumptions?.[0] && (
                  <div className="preview-line">
                    <Leaf size={13} className="prev-icon env" />
                    <span>{item.plan.environmental_assumptions[0]}</span>
                  </div>
                )}
              </div>

              <div className="card-bottom-row">
                <span className="steps-count">
                  {item.plan.action_steps?.length || 5} Sequenced SOP Steps
                </span>
                <button
                  className="view-full-plan-btn"
                  onClick={() => onOpenPlan(item, item.plan)}
                >
                  <span>View Protocol &rarr;</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
