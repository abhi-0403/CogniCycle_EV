import React from "react";
import {
  Package,
  Recycle,
  Wrench,
  Activity,
  ArrowUpRight,
  TrendingUp,
  DollarSign,
  Leaf,
  Boxes,
  UploadCloud,
  FileCheck2,
  Sparkles,
  ShieldCheck,
  Lightbulb,
  ArrowRight
} from "lucide-react";
import "./OverviewView.css";

export default function OverviewView({
  stats,
  datasetCount,
  datasetSource,
  recentDecisions = [],
  onNavigateTab,
  onTakeAction,
  onInspectItem,
  onOpenRationale
}) {
  const reusePct = stats.total ? Math.round((stats.reuse / stats.total) * 100) : 0;
  const refurbishPct = stats.total ? Math.round((stats.refurbish / stats.total) * 100) : 0;
  const recyclePct = stats.total ? Math.round((stats.recycle / stats.total) * 100) : 0;
  const assessPct = stats.total ? Math.round((stats.assessmentRequired / stats.total) * 100) : 0;

  return (
    <div className="overview-view-container">
      {/* Hero Welcome Banner */}
      <div className="hero-banner">
        <div className="hero-left">
          <div className="hero-pill">
            <ShieldCheck size={13} className="hero-zap" />
            <span>Audited Component Lifecycle Intelligence</span>
          </div>
          <h1>End-of-Life EV Intelligence & Circular Triage</h1>
          <p>
            Automated circular disposition routing across the 7 EV component pillars, critical mineral conservation analytics, and grounded engineering action protocols.
          </p>
        </div>

        <div className="hero-quick-stats">
          <div className="quick-stat-box">
            <span className="q-label">Audited Fleet Size</span>
            <span className="q-val">{stats.total || datasetCount} Units</span>
          </div>
          <div className="quick-stat-box">
            <span className="q-label">Circularity Yield</span>
            <span className="q-val">{reusePct + refurbishPct}%</span>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="kpi-cards-grid">
        <div className="metric-card">
          <div className="m-card-header">
            <span className="m-label">TOTAL ASSETS</span>
            <div className="m-icon-box m-icon-default">
              <Package size={18} />
            </div>
          </div>
          <div className="m-card-body">
            <span className="m-val">{stats.total || "—"}</span>
            <span className="m-sub">7 Component Pillars Evaluated</span>
          </div>
        </div>

        <div className="metric-card border-green">
          <div className="m-card-header">
            <span className="m-label">DIRECT REUSE</span>
            <div className="m-icon-box m-icon-green">
              <ArrowUpRight size={18} />
            </div>
          </div>
          <div className="m-card-body">
            <span className="m-val text-green">{stats.reuse || 0}</span>
            <span className="m-sub">{reusePct}% 2nd-life deployment</span>
          </div>
        </div>

        <div className="metric-card border-blue">
          <div className="m-card-header">
            <span className="m-label">REFURBISH</span>
            <div className="m-icon-box m-icon-blue">
              <Wrench size={18} />
            </div>
          </div>
          <div className="m-card-body">
            <span className="m-val text-blue">{stats.refurbish || 0}</span>
            <span className="m-sub">{refurbishPct}% precision remanufacturing</span>
          </div>
        </div>

        <div className="metric-card border-amber">
          <div className="m-card-header">
            <span className="m-label">RECYCLE</span>
            <div className="m-icon-box m-icon-amber">
              <Recycle size={18} />
            </div>
          </div>
          <div className="m-card-body">
            <span className="m-val text-amber">{stats.recycle || 0}</span>
            <span className="m-sub">{recyclePct}% closed-loop recovery</span>
          </div>
        </div>

        <div className="metric-card border-red">
          <div className="m-card-header">
            <span className="m-label">ASSESSMENT REQ.</span>
            <div className="m-icon-box m-icon-red">
              <Activity size={18} />
            </div>
          </div>
          <div className="m-card-body">
            <span className="m-val text-red">{stats.assessmentRequired || 0}</span>
            <span className="m-sub">{assessPct}% laboratory diagnostics</span>
          </div>
        </div>
      </div>

      {/* Disposition Distribution Bar */}
      <div className="disposition-bar-card">
        <div className="bar-card-header">
          <h4>Fleet Disposition Share</h4>
          <span className="bar-total-label">{stats.total} Components Evaluated</span>
        </div>

        <div className="progress-stacked-bar">
          <div
            className="bar-segment seg-reuse"
            style={{ width: `${reusePct}%` }}
            title={`Reuse: ${stats.reuse} (${reusePct}%)`}
          />
          <div
            className="bar-segment seg-refurbish"
            style={{ width: `${refurbishPct}%` }}
            title={`Refurbish: ${stats.refurbish} (${refurbishPct}%)`}
          />
          <div
            className="bar-segment seg-recycle"
            style={{ width: `${recyclePct}%` }}
            title={`Recycle: ${stats.recycle} (${recyclePct}%)`}
          />
          <div
            className="bar-segment seg-assess"
            style={{ width: `${assessPct}%` }}
            title={`Assessment: ${stats.assessmentRequired} (${assessPct}%)`}
          />
        </div>

        <div className="bar-legend">
          <div className="legend-item">
            <span className="legend-dot dot-reuse" />
            <span>Reuse ({stats.reuse})</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot dot-refurbish" />
            <span>Refurbish ({stats.refurbish})</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot dot-recycle" />
            <span>Recycle ({stats.recycle})</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot dot-assess" />
            <span>Assessment Required ({stats.assessmentRequired})</span>
          </div>
        </div>
      </div>

      {/* Action shortcuts & Recent Stream */}
      <div className="overview-split-grid">
        {/* Navigation Launchers */}
        <div className="action-launchers-col">
          <h3 className="col-title">Platform Quick Actions</h3>

          <div
            className="launcher-card"
            onClick={() => onNavigateTab("triage")}
          >
            <div className="launcher-icon l-green">
              <Boxes size={20} />
            </div>
            <div className="launcher-info">
              <h4>Triage & Inventory Explorer</h4>
              <p>Search, filter, and inspect {stats.total} components with grounded action protocols.</p>
            </div>
            <ArrowRight size={18} className="launcher-arrow" />
          </div>

          <div
            className="launcher-card"
            onClick={() => onNavigateTab("upload")}
          >
            <div className="launcher-icon l-blue">
              <UploadCloud size={20} />
            </div>
            <div className="launcher-info">
              <h4>Ingest Custom Asset Dataset</h4>
              <p>Upload JSON telemetry datasets to execute automated circular routing.</p>
            </div>
            <ArrowRight size={18} className="launcher-arrow" />
          </div>

          <div
            className="launcher-card"
            onClick={() => onNavigateTab("action_plans")}
          >
            <div className="launcher-icon l-purple">
              <FileCheck2 size={20} />
            </div>
            <div className="launcher-info">
              <h4>Verified Action Protocols Archive</h4>
              <p>Review and export standardized engineering and economic SOPs.</p>
            </div>
            <ArrowRight size={18} className="launcher-arrow" />
          </div>
        </div>

        {/* Recent Stream */}
        <div className="recent-stream-col">
          <div className="stream-header">
            <h3 className="col-title">Recent Inbound Telemetry</h3>
            <button
              className="view-all-link"
              onClick={() => onNavigateTab("triage")}
            >
              View Full Table &rarr;
            </button>
          </div>

          <div className="stream-list">
            {recentDecisions.slice(0, 5).map((item) => (
              <div key={item.asset_id} className="stream-item">
                <div className="stream-item-main">
                  <div className="stream-id-row">
                    <span className="stream-id">{item.asset_id}</span>
                    <button
                      className={`disposition-lighten-btn small ${item.decision?.toLowerCase()}`}
                      onClick={() => onOpenRationale && onOpenRationale(item)}
                      title="Click to view decision rationale"
                    >
                      <Lightbulb size={10} className="lighten-bulb-icon" />
                      <span>{item.decision}</span>
                    </button>
                  </div>
                  <strong className="stream-comp-name">{item.component}</strong>
                  <span className="stream-meta">
                    {item.raw_asset?.vehicle_make} {item.raw_asset?.vehicle_model} &bull;{" "}
                    {item.raw_asset?.diagnostic_data?.soh !== undefined
                      ? `${item.raw_asset.diagnostic_data.soh}% SOH`
                      : "Verified"} &bull;{" "}
                    {item.raw_asset?.technical_data?.weight_kg || 25} kg
                  </span>
                </div>

                <div className="stream-actions">
                  <button
                    className="stream-action-btn"
                    onClick={() => onTakeAction(item)}
                  >
                    <Sparkles size={13} />
                    <span>Action</span>
                  </button>
                  <button
                    className="stream-inspect-btn"
                    onClick={() => onInspectItem(item)}
                  >
                    Inspect
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
