import React, { useState, useMemo } from "react";
import {
  Search,
  Filter,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Info,
  Layers,
  Lightbulb,
  CheckCircle2,
  FileText
} from "lucide-react";
import "./TriageExplorerView.css";

export default function TriageExplorerView({
  decisions = [],
  savedPlans = {},
  onTakeAction,
  onInspectItem,
  onOpenRationale
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterDecision, setFilterDecision] = useState("ALL");
  const [pageSize, setPageSize] = useState(25);
  const [currentPage, setCurrentPage] = useState(1);

  // Filter and search
  const filteredList = useMemo(() => {
    let list = decisions;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter((d) => {
        const raw = d.raw_asset || {};
        const vMake = (raw.vehicle_make || "").toLowerCase();
        const vModel = (raw.vehicle_model || "").toLowerCase();
        const tech = (raw.technical_data?.technology || "").toLowerCase();
        const id = (d.asset_id || "").toLowerCase();
        const comp = (d.component || "").toLowerCase();
        const dec = (d.decision || "").toLowerCase();
        const domain = (d.domain || "").toLowerCase();

        return (
          id.includes(q) ||
          comp.includes(q) ||
          dec.includes(q) ||
          domain.includes(q) ||
          vMake.includes(q) ||
          vModel.includes(q) ||
          tech.includes(q)
        );
      });
    }

    if (filterDecision !== "ALL") {
      list = list.filter((d) => d.decision === filterDecision);
    }

    return list;
  }, [decisions, searchQuery, filterDecision]);

  // Pagination calculations
  const totalItems = filteredList.length;
  const effectivePageSize = pageSize === "ALL" ? totalItems : pageSize;
  const totalPages = Math.ceil(totalItems / (effectivePageSize || 1)) || 1;

  const paginatedList = useMemo(() => {
    if (pageSize === "ALL") return filteredList;
    const startIndex = (currentPage - 1) * pageSize;
    return filteredList.slice(startIndex, startIndex + pageSize);
  }, [filteredList, currentPage, pageSize]);

  const handleFilterChange = (filter) => {
    setFilterDecision(filter);
    setCurrentPage(1);
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  return (
    <div className="triage-explorer-container">
      {/* Header & Controls */}
      <div className="explorer-header">
        <div>
          <div className="explorer-tagline">
            <Layers size={14} className="tag-icon" />
            <span>TRIAGE INVENTORY REPOSITORY</span>
          </div>
          <h2>Circular Triage & Asset Explorer</h2>
          <p>
            Explore all {decisions.length} operational components across 7 vehicle pillars with verified telemetry, safety classifications, and grounded engineering protocols.
          </p>
        </div>

        {/* Search Bar */}
        <div className="explorer-search-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="explorer-search-input"
            placeholder="Search by ID, component, make, model..."
            value={searchQuery}
            onChange={handleSearchChange}
          />
        </div>
      </div>

      {/* Filter and View Bar */}
      <div className="explorer-controls-bar">
        <div className="filter-pill-group">
          {["ALL", "REUSE", "REFURBISH", "RECYCLE", "ASSESSMENT_REQUIRED"].map((f) => (
            <button
              key={f}
              className={`filter-pill ${filterDecision === f ? "active" : ""}`}
              onClick={() => handleFilterChange(f)}
            >
              {f.replace("_", " ")}
            </button>
          ))}
        </div>

        <div className="pagination-controls">
          <span className="results-label">
            Showing {filteredList.length === 0 ? 0 : (currentPage - 1) * effectivePageSize + 1} -{" "}
            {Math.min(currentPage * effectivePageSize, totalItems)} of {totalItems} items
          </span>

          <div className="page-size-selector">
            <span>Rows:</span>
            <select
              value={pageSize}
              onChange={(e) => {
                const val = e.target.value;
                setPageSize(val === "ALL" ? "ALL" : Number(val));
                setCurrentPage(1);
              }}
            >
              <option value={15}>15</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value="ALL">All ({totalItems})</option>
            </select>
          </div>

          {pageSize !== "ALL" && (
            <div className="page-nav-buttons">
              <button
                className="nav-page-btn"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              >
                <ChevronLeft size={16} />
              </button>
              <span className="page-num-indicator">
                {currentPage} / {totalPages}
              </span>
              <button
                className="nav-page-btn"
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Components Table */}
      <div className="triage-table-wrapper">
        <table className="triage-table">
          <thead>
            <tr>
              <th style={{ width: "120px" }}>Asset ID</th>
              <th>Component & Platform</th>
              <th>Domain / Tech</th>
              <th style={{ width: "110px" }}>Telemetry</th>
              <th style={{ width: "160px" }}>
                <span>Disposition</span>
                <span className="th-hint" title="Click any badge to view the Decision Engine rationale">(Click for Rationale)</span>
              </th>
              <th style={{ width: "90px" }}>Confidence</th>
              <th style={{ width: "190px", textAlign: "right" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {paginatedList.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-row">
                  No components match the current search & filter criteria.
                </td>
              </tr>
            ) : (
              paginatedList.map((item) => {
                const raw = item.raw_asset || {};
                const diag = raw.diagnostic_data || {};
                const tech = raw.technical_data || {};
                const vehicle = `${raw.vehicle_make || ""} ${raw.vehicle_model || ""}`.trim();
                const isCachedPlan = Boolean(savedPlans[item.asset_id]);

                return (
                  <tr key={item.asset_id || Math.random()}>
                    {/* Asset ID */}
                    <td>
                      <span className="mono-asset-id">{item.asset_id}</span>
                    </td>

                    {/* Component */}
                    <td>
                      <div className="comp-col">
                        <strong className="comp-name">{item.component}</strong>
                        <span className="comp-sub">
                          {vehicle ? `${vehicle} • ` : ""}
                          {raw.manufacturer || "OEM"} {raw.model || ""}
                        </span>
                      </div>
                    </td>

                    {/* Domain & Tech */}
                    <td>
                      <div className="tech-col">
                        <span className="domain-name">{item.domain || "EV"}</span>
                        <span className="tech-badge">{tech.technology || "Automotive"}</span>
                      </div>
                    </td>

                    {/* Telemetry */}
                    <td>
                      <div className="diag-col">
                        <span
                          className={`soh-val ${
                            diag.soh >= 80 ? "soh-high" : diag.soh >= 65 ? "soh-mid" : "soh-low"
                          }`}
                        >
                          {diag.soh !== undefined ? `${diag.soh}% SOH` : "Pass"}
                        </span>
                        <span className="cycle-sub">
                          {diag.cycle_count ? `${diag.cycle_count.toLocaleString()} cyc` : (tech.weight_kg ? `${tech.weight_kg} kg` : "")}
                        </span>
                      </div>
                    </td>

                    {/* Disposition Badge with Lighten Interactive Rationale */}
                    <td>
                      <button
                        className={`disposition-lighten-btn ${item.decision?.toLowerCase()}`}
                        onClick={() => onOpenRationale && onOpenRationale(item)}
                        title={`Click to view why this ${item.component} was routed to ${item.decision}`}
                      >
                        <Lightbulb size={12} className="lighten-bulb-icon" />
                        <span>{item.decision}</span>
                      </button>
                    </td>

                    {/* Confidence */}
                    <td>
                      <span className="confidence-pill">
                        {Math.round((item.confidence || 0.85) * 100)}%
                      </span>
                    </td>

                    {/* Actions */}
                    <td style={{ textAlign: "right" }}>
                      <div className="table-actions-cell">
                        <button
                          className="btn-inspect"
                          onClick={() => onInspectItem(item)}
                          title="View complete diagnostic and technical data"
                        >
                          Inspect
                        </button>

                        <button
                          className={`btn-take-action ${isCachedPlan ? "has-saved-plan" : ""}`}
                          onClick={() => onTakeAction(item)}
                          title="View or generate tailored standard operating protocol"
                        >
                          {isCachedPlan ? (
                            <>
                              <FileText size={13} />
                              <span>Protocol Ready</span>
                            </>
                          ) : (
                            <>
                              <Sparkles size={13} />
                              <span>Take Action</span>
                            </>
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
