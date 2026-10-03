import React, { useState } from "react";
import {
  X,
  Sparkles,
  DollarSign,
  Leaf,
  CheckCircle2,
  Copy,
  Check,
  RefreshCw,
  ShieldCheck,
  FileCheck2
} from "lucide-react";
import "./ActionPlanModal.css";

export default function ActionPlanModal({
  isOpen,
  onClose,
  item,
  plan,
  isGenerating,
  onRegenerate
}) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !item) return null;

  const raw = item.raw_asset || {};
  const vehicle = `${raw.vehicle_make || ""} ${raw.vehicle_model || ""}`.trim() || "EV Platform";
  const mfr = raw.manufacturer || "OEM";
  const model = raw.model || "";
  const weight = raw.technical_data?.weight_kg || 25;

  const handleCopy = () => {
    if (!plan) return;
    const content = `COGNICYCLE EV - COMPONENT ACTION PROTOCOL
==================================================
Asset ID: ${item.asset_id || "N/A"}
Component: ${item.component || "N/A"}
Vehicle: ${vehicle} (${mfr} ${model})
Weight: ${weight} kg
Disposition: ${item.decision || "N/A"}
Safety Status: ${item.safety_status || "SAFE"}
Confidence: ${Math.round((item.confidence || 0) * 100)}%
Standard: DPP Certified Remanufacturing Protocol

PROTOCOL HEADLINE:
${plan.headline || ""}

ECONOMIC ASSUMPTIONS & VIABILITY:
${(plan.economic_assumptions || []).map((a) => `• ${a}`).join("\n")}

ENVIRONMENTAL ASSUMPTIONS & IMPACT:
${(plan.environmental_assumptions || []).map((a) => `• ${a}`).join("\n")}

STANDARD OPERATING PROCEDURE (SOP) ACTION STEPS:
${(plan.action_steps || [])
  .map((s) => `Step ${s.step}: ${s.title}\n  ${s.description}`)
  .join("\n\n")}
`;
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2200);
  };

  return (
    <div className="action-modal-overlay" onClick={onClose}>
      <div
        className="action-modal-container"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="action-modal-header">
          <div className="action-modal-title-area">
            <div className="action-modal-tagline">
              <Sparkles size={14} className="sparkle-icon" />
              <span>Grounded Circular Action Protocol</span>
              <span className="source-pill verified-pill" title="Certified Standard Operating Procedure">
                <ShieldCheck size={12} />
                DPP Certified SOP
              </span>
            </div>

            <h2 className="action-modal-title">
              {item.component} &bull; <span className="mono-id">{item.asset_id}</span>
            </h2>

            <div className="action-modal-meta-row">
              <span className="meta-item">
                <strong>Platform:</strong> {vehicle}
              </span>
              <span className="meta-separator">&bull;</span>
              <span className="meta-item">
                <strong>Spec:</strong> {mfr} {model}
              </span>
              <span className="meta-separator">&bull;</span>
              <span className="meta-item">
                <strong>Weight:</strong> {weight} kg
              </span>
              <span className="meta-separator">&bull;</span>
              <span className="meta-item">
                <strong>SOH:</strong> {raw.diagnostic_data?.soh !== undefined ? `${raw.diagnostic_data.soh}%` : "Nominal"}
              </span>
              <span className="meta-separator">&bull;</span>
              <span className={`disposition-tag ${item.decision?.toLowerCase()}`}>
                {item.decision}
              </span>
            </div>
          </div>

          <button
            className="action-modal-close-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content body */}
        <div className="action-modal-content">
          {isGenerating ? (
            <div className="action-modal-loading">
              <div className="loading-orbit">
                <RefreshCw size={28} className="spin" />
              </div>
              <h3>Synthesizing Grounded Action Protocol...</h3>
              <p>
                Synthesizing engineering steps tailored to {item.component} ({weight} kg) diagnostic telemetry, degradation physics, and circular economics.
              </p>
            </div>
          ) : plan ? (
            <div className="action-plan-layout">
              {/* Protocol Headline */}
              <div className="plan-headline-box">
                <div className="headline-badge">STANDARD OPERATING PROCEDURE</div>
                <p className="headline-text">{plan.headline}</p>
              </div>

              {/* Economic & Environmental Grid */}
              <div className="plan-assumptions-grid">
                {/* Economic */}
                <div className="assumption-card economic-card">
                  <div className="assumption-header">
                    <div className="assumption-icon econ-icon">
                      <DollarSign size={16} />
                    </div>
                    <div>
                      <h4>Economic Assumptions</h4>
                      <span>Grounded cost-benefit & salvage valuation</span>
                    </div>
                  </div>
                  <ul className="assumption-list">
                    {(plan.economic_assumptions || []).map((itemText, idx) => (
                      <li key={idx}>
                        <CheckCircle2 size={14} className="list-check econ-check" />
                        <span>{itemText}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Environmental */}
                <div className="assumption-card environmental-card">
                  <div className="assumption-header">
                    <div className="assumption-icon env-icon">
                      <Leaf size={16} />
                    </div>
                    <div>
                      <h4>Environmental Assumptions</h4>
                      <span>Decarbonization & raw mineral conservation</span>
                    </div>
                  </div>
                  <ul className="assumption-list">
                    {(plan.environmental_assumptions || []).map((itemText, idx) => (
                      <li key={idx}>
                        <CheckCircle2 size={14} className="list-check env-check" />
                        <span>{itemText}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Action Steps */}
              <div className="action-steps-section">
                <h4 className="section-title">Standard Operating Procedure (SOP) Action Steps</h4>
                <div className="action-steps-timeline">
                  {(plan.action_steps || []).map((stepObj) => (
                    <div key={stepObj.step} className="step-card">
                      <div className="step-number-col">
                        <span className="step-badge">Step {stepObj.step}</span>
                        {stepObj.step < (plan.action_steps || []).length && (
                          <div className="step-line" />
                        )}
                      </div>
                      <div className="step-body">
                        <h5 className="step-title">{stepObj.title}</h5>
                        <p className="step-desc">{stepObj.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="action-modal-empty">
              <p>No action plan available for this item.</p>
            </div>
          )}
        </div>

        {/* Footer controls */}
        <div className="action-modal-footer">
          <div className="footer-left-info">
            <span className="storage-hint">
              Digital Product Passport ID: <code className="code-pill">DPP-{item.asset_id}</code>
            </span>
          </div>

          <div className="footer-actions">
            <button
              className="secondary-btn regenerate-btn"
              onClick={() => onRegenerate && onRegenerate(item)}
              disabled={isGenerating}
              title="Re-run evaluation model"
            >
              <RefreshCw size={14} className={isGenerating ? "spin" : ""} />
              <span>Re-evaluate Protocol</span>
            </button>

            <button
              className="primary-btn copy-btn"
              onClick={handleCopy}
              disabled={!plan || isGenerating}
            >
              {copied ? <Check size={15} /> : <Copy size={15} />}
              <span>{copied ? "Copied to Clipboard!" : "Copy Protocol Report"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
