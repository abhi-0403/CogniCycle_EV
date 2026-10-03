import React from "react";
import {
  LayoutDashboard,
  Boxes,
  UploadCloud,
  FileCheck2,
  LineChart,
  RefreshCw,
  ShieldCheck,
  Leaf
} from "lucide-react";
import "./Navbar.css";

export default function Navbar({
  activeTab,
  setActiveTab,
  stats,
  datasetSource,
  datasetCount,
  isLoading,
  onRefresh,
  savedPlansCount = 0
}) {
  const navItems = [
    {
      id: "overview",
      label: "Overview",
      icon: <LayoutDashboard size={17} />,
      badge: null
    },
    {
      id: "triage",
      label: "Triage Explorer",
      icon: <Boxes size={17} />,
      badge: datasetCount > 0 ? `${datasetCount}` : null
    },
    {
      id: "upload",
      label: "Upload Dataset",
      icon: <UploadCloud size={17} />,
      badge: "JSON"
    },
    {
      id: "action_plans",
      label: "Action Plans",
      icon: <FileCheck2 size={17} />,
      badge: savedPlansCount > 0 ? `${savedPlansCount} Saved` : null,
      badgeColor: "success"
    },
    {
      id: "analytics",
      label: "Circular Analytics",
      icon: <LineChart size={17} />,
      badge: null
    }
  ];

  return (
    <header className="navbar-container">
      <div className="navbar-inner">
        {/* Brand identity */}
        <div className="navbar-brand" onClick={() => setActiveTab("overview")}>
          <div className="brand-logo-glow">
            <Leaf size={20} className="brand-icon" />
          </div>
          <div className="brand-text">
            <div className="brand-title-row">
              <span className="brand-title">CogniCycle</span>
              <span className="brand-badge-ev">EV</span>
            </div>
            <span className="brand-subtitle">End-of-Life Circular Triage Platform</span>
          </div>
        </div>

        {/* Navigation tabs */}
        <nav className="navbar-tabs" aria-label="Main Navigation">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                id={`nav-tab-${item.id}`}
                className={`nav-tab-btn ${isActive ? "active" : ""}`}
                onClick={() => setActiveTab(item.id)}
              >
                <span className="nav-tab-icon">{item.icon}</span>
                <span className="nav-tab-label">{item.label}</span>
                {item.badge && (
                  <span
                    className={`nav-tab-badge ${
                      item.badgeColor === "success" ? "badge-success" : ""
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* System & Compliance status indicators */}
        <div className="navbar-actions">
          <div className="cache-pill" title="DPP Registry Audit Status">
            <ShieldCheck size={14} className="zap-icon" />
            <span className="cache-label">
              {datasetSource === "cache"
                ? "System Synchronized"
                : datasetSource === "uploaded"
                ? "Custom Batch"
                : "Active Ingestion"}
            </span>
          </div>

          <button
            className={`sync-btn ${isLoading ? "spinning" : ""}`}
            onClick={onRefresh}
            disabled={isLoading}
            title="Synchronize and re-evaluate telemetry"
          >
            <RefreshCw size={14} className={isLoading ? "spin" : ""} />
            <span>{isLoading ? "Syncing..." : "Sync"}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
