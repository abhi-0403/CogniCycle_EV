import React, { useState, useRef } from "react";
import {
  UploadCloud,
  FileCheck,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  Sparkles,
  ArrowRight,
  Database,
  Layers,
  FileText
} from "lucide-react";
import "./UploadView.css";

export default function UploadView({ onDatasetUploaded, onSwitchToExplorer }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [parseError, setParseError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFile = (file) => {
    if (!file) return;
    if (!file.name.endsWith(".json")) {
      setParseError("Please select a valid JSON file (.json).");
      setSelectedFile(null);
      setParsedData(null);
      return;
    }

    setSelectedFile(file);
    setParseError(null);
    setUploadSuccess(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const json = JSON.parse(text);
        
        let assetList = [];
        if (Array.isArray(json)) {
          assetList = json;
        } else if (json.assets && Array.isArray(json.assets)) {
          assetList = json.assets;
        } else {
          throw new Error("JSON structure must contain an array of asset objects or an 'assets' array.");
        }

        if (assetList.length === 0) {
          throw new Error("The uploaded JSON file contains 0 components.");
        }

        // Normalize assets (ensure asset_id exists)
        const normalized = assetList.map((item, idx) => ({
          ...item,
          asset_id: item.asset_id || `EV-UP-${String(idx + 1).padStart(3, "0")}`
        }));

        setParsedData(normalized);
      } catch (err) {
        setParseError(`JSON Parse Error: ${err.message}`);
        setParsedData(null);
      }
    };
    reader.onerror = () => {
      setParseError("Failed to read file.");
    };
    reader.readAsText(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const handleUploadAndTriage = async () => {
    if (!parsedData || parsedData.length === 0) return;

    setIsProcessing(true);
    setProcessingStage("Ingesting dataset and verifying schemas...");

    try {
      setProcessingStage("Executing 7-pillar telemetry routing and circular disposition engine...");
      
      const response = await fetch("http://localhost:8000/assets/upload-json", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: selectedFile?.name || "custom_dataset.json",
          assets: parsedData
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      setProcessingStage("Finalizing circular audit and registering records...");
      const result = await response.json();

      setUploadSuccess({
        count: result.count,
        filename: result.filename
      });

      if (onDatasetUploaded) {
        onDatasetUploaded(result.data, "uploaded");
      }
    } catch (err) {
      setParseError(`Triage Pipeline Error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLoadSampleData = async () => {
    setIsProcessing(true);
    setProcessingStage("Loading verified 105 EV component benchmark dataset...");
    setParseError(null);
    setUploadSuccess(null);

    try {
      const res = await fetch("http://localhost:8000/assets/triage/rerun", {
        method: "POST"
      });
      const data = await res.json();
      
      setUploadSuccess({
        count: data.data.length,
        filename: "verified_ev_benchmark_105.json"
      });

      if (onDatasetUploaded) {
        onDatasetUploaded(data.data, "cache");
      }
    } catch (err) {
      setParseError(`Failed to load benchmark dataset: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="upload-view-container">
      <div className="upload-header">
        <div className="upload-tagline">
          <Database size={14} className="tag-icon" />
          <span>DATASET INGESTION & PIPELINE</span>
        </div>
        <h2>Ingest Custom EV Component Dataset</h2>
        <p>
          Upload your JSON dataset of decommissioned EV batteries, inverters, traction motors, power electronics, and compute modules.
          The automated triage engine evaluates telemetry, routes through the 7 automotive pillars, and determines grounded circular pathways.
        </p>
      </div>

      {uploadSuccess ? (
        <div className="upload-success-card">
          <div className="success-icon-box">
            <CheckCircle2 size={32} />
          </div>
          <h3>Circular Triage Successfully Completed</h3>
          <p>
            Successfully evaluated and registered <strong>{uploadSuccess.count} components</strong> into the circular inventory.
          </p>
          <div className="success-actions">
            <button className="btn-explorer" onClick={onSwitchToExplorer}>
              <span>Explore Ingested Assets in Triage</span>
              <ArrowRight size={16} />
            </button>
            <button
              className="btn-upload-another"
              onClick={() => {
                setSelectedFile(null);
                setParsedData(null);
                setUploadSuccess(null);
              }}
            >
              Upload Another Dataset
            </button>
          </div>
        </div>
      ) : (
        <div className="upload-workspace">
          {/* Dropzone Area */}
          <div
            className={`dropzone-box ${dragActive ? "drag-active" : ""}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              style={{ display: "none" }}
              onChange={handleChange}
            />

            <div className="dropzone-icon-circle">
              <UploadCloud size={32} />
            </div>

            <h3>Drag & Drop your JSON Asset Dataset here</h3>
            <p>or click to browse local files on your computer</p>

            <span className="file-format-badge">Supported Format: JSON (.json)</span>
          </div>

          {/* Error Banner */}
          {parseError && (
            <div className="parse-error-banner">
              <AlertCircle size={18} />
              <span>{parseError}</span>
            </div>
          )}

          {/* File Selected & Preview */}
          {parsedData && (
            <div className="file-preview-card">
              <div className="preview-header">
                <div className="file-info-col">
                  <FileText size={20} className="file-icon" />
                  <div>
                    <h4>{selectedFile?.name || "Uploaded Dataset"}</h4>
                    <span>
                      {(selectedFile?.size / 1024).toFixed(1)} KB &bull;{" "}
                      <strong>{parsedData.length} EV Components Detected</strong>
                    </span>
                  </div>
                </div>

                <button
                  className="start-triage-btn"
                  onClick={handleUploadAndTriage}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <RefreshCw size={15} className="spin" />
                      <span>{processingStage || "Processing..."}</span>
                    </>
                  ) : (
                    <>
                      <Sparkles size={15} />
                      <span>Run Circular Triage Pipeline</span>
                    </>
                  )}
                </button>
              </div>

              {/* Sample preview table */}
              <div className="sample-preview">
                <span className="sample-label">First 3 Sample Components:</span>
                <div className="sample-items-grid">
                  {parsedData.slice(0, 3).map((item, i) => (
                    <div key={i} className="sample-item-card">
                      <span className="sample-id">{item.asset_id}</span>
                      <strong className="sample-comp">{item.component || "Component"}</strong>
                      <span className="sample-tech">
                        {item.technical_data?.technology || "EV Domain"} &bull;{" "}
                        {item.technical_data?.weight_kg ? `${item.technical_data.weight_kg} kg` : "Nominal Weight"} &bull;{" "}
                        SOH: {item.diagnostic_data?.soh !== undefined ? `${item.diagnostic_data.soh}%` : "N/A"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Quick Benchmark Option */}
          <div className="benchmark-card">
            <div className="benchmark-info">
              <h4>Want to test with the standard 105 EV component benchmark dataset?</h4>
              <p>
                Includes batteries, inverters, motors, OBCs, and ECUs with realistic automotive weights, market valuations, and unique IDs.
              </p>
            </div>
            <button
              className="benchmark-btn"
              onClick={handleLoadSampleData}
              disabled={isProcessing}
            >
              <Database size={15} />
              <span>Load 105 Component Benchmark</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
