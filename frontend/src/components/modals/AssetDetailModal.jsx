import React from "react";
import {
  X,
  Cpu,
  Activity,
  DollarSign,
  ShieldCheck,
  ShieldAlert,
  BatteryCharging,
  Gauge,
  Thermometer,
  Layers,
  Wrench
} from "lucide-react";
import "./AssetDetailModal.css";

export default function AssetDetailModal({ isOpen, onClose, item, onTakeAction }) {
  if (!isOpen || !item) return null;

  const raw = item.raw_asset || {};
  const tech = raw.technical_data || {};
  const diag = raw.diagnostic_data || {};
  const econ = raw.economic_data || {};
  const vehicle = `${raw.vehicle_make || ""} ${raw.vehicle_model || ""}`.trim() || "EV Vehicle";

  return (
    <div className="detail-modal-overlay" onClick={onClose}>
      <div
        className="detail-modal-container"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="detail-modal-header">
          <div className="detail-header-left">
            <span className="mono-pill">{item.asset_id}</span>
            <h3 className="detail-title">{item.component}</h3>
            <span className="detail-subtitle">{vehicle} &bull; {raw.manufacturer} {raw.model}</span>
          </div>

          <div className="detail-header-right">
            <span className={`disposition-badge ${item.decision?.toLowerCase()}`}>
              {item.decision}
            </span>
            <button className="detail-close-btn" onClick={onClose}>
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="detail-modal-body">
          {/* Diagnostic section */}
          <div className="detail-section">
            <h4 className="detail-section-title">
              <Activity size={15} /> Diagnostic & Degradation Telemetry
            </h4>
            <div className="telemetry-grid">
              <div className="telemetry-card">
                <span className="telemetry-label">State of Health (SOH)</span>
                <span className={`telemetry-val ${diag.soh >= 80 ? "val-good" : diag.soh >= 65 ? "val-med" : "val-low"}`}>
                  {diag.soh !== undefined ? `${diag.soh}%` : "N/A"}
                </span>
              </div>
              <div className="telemetry-card">
                <span className="telemetry-label">Cycle Count</span>
                <span className="telemetry-val">{diag.cycle_count?.toLocaleString() ?? "N/A"}</span>
              </div>
              <div className="telemetry-card">
                <span className="telemetry-label">Internal Resistance</span>
                <span className="telemetry-val">{diag.internal_resistance_mohm ? `${diag.internal_resistance_mohm} mΩ` : "N/A"}</span>
              </div>
              <div className="telemetry-card">
                <span className="telemetry-label">Nominal Capacity</span>
                <span className="telemetry-val">{diag.nominal_capacity_kwh ? `${diag.nominal_capacity_kwh} kWh` : "N/A"}</span>
              </div>
              <div className="telemetry-card">
                <span className="telemetry-label">Peak Temperature</span>
                <span className="telemetry-val">{diag.max_recorded_temp_c ? `${diag.max_recorded_temp_c}°C` : "N/A"}</span>
              </div>
              <div className="telemetry-card">
                <span className="telemetry-label">Fault Codes</span>
                <span className="telemetry-val mono-small">
                  {diag.fault_codes && diag.fault_codes.length > 0 ? diag.fault_codes.join(", ") : "None Detected"}
                </span>
              </div>
            </div>
          </div>

          {/* Technical Specifications */}
          <div className="detail-section">
            <h4 className="detail-section-title">
              <Cpu size={15} /> Technical Specifications
            </h4>
            <div className="spec-table">
              <div className="spec-row">
                <span className="spec-key">Domain</span>
                <span className="spec-val">{item.domain || "N/A"}</span>
              </div>
              <div className="spec-row">
                <span className="spec-key">Technology / Chemistry</span>
                <span className="spec-val">{tech.technology || "N/A"}</span>
              </div>
              <div className="spec-row">
                <span className="spec-key">Mass / Weight</span>
                <span className="spec-val">{tech.weight_kg ? `${tech.weight_kg} kg` : "N/A"}</span>
              </div>
              <div className="spec-row">
                <span className="spec-key">Dimensions (L×W×H)</span>
                <span className="spec-val">{tech.dimensions_mm ? `${tech.dimensions_mm.join(" × ")} mm` : "N/A"}</span>
              </div>
              <div className="spec-row">
                <span className="spec-key">Ingress Protection</span>
                <span className="spec-val">{tech.ip_rating || "N/A"}</span>
              </div>
              <div className="spec-row">
                <span className="spec-key">Hazard Classification</span>
                <span className="spec-val">{tech.hazardous_classification || "Low"}</span>
              </div>
            </div>
          </div>

          {/* Economic Data */}
          <div className="detail-section">
            <h4 className="detail-section-title">
              <DollarSign size={15} /> Economic Valuation
            </h4>
            <div className="telemetry-grid">
              <div className="telemetry-card">
                <span className="telemetry-label">Secondary Reuse Value</span>
                <span className="telemetry-val val-good">${econ.reuse_value?.toLocaleString() ?? "—"}</span>
              </div>
              <div className="telemetry-card">
                <span className="telemetry-label">Refurbished Market Value</span>
                <span className="telemetry-val">${econ.refurbishment_value?.toLocaleString() ?? "—"}</span>
              </div>
              <div className="telemetry-card">
                <span className="telemetry-label">Estimated Repair Cost</span>
                <span className="telemetry-val">${econ.estimated_repair_cost?.toLocaleString() ?? "—"}</span>
              </div>
              <div className="telemetry-card">
                <span className="telemetry-label">Raw Material Scrap Value</span>
                <span className="telemetry-val">${econ.recovery_value?.toLocaleString() ?? "—"}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="detail-modal-footer">
          <button className="detail-btn secondary" onClick={onClose}>
            Close
          </button>
          <button
            className="detail-btn primary"
            onClick={() => {
              onClose();
              if (onTakeAction) onTakeAction(item);
            }}
          >
            Take Action Protocol &rarr;
          </button>
        </div>
      </div>
    </div>
  );
}
