# ⚡ CogniCycle EV — AI-Driven EV E-Waste Triage Platform

**CogniCycle EV** is an enterprise-grade end-of-life (EOL) electric vehicle battery and electronics circular triage platform. It ingests decommissioned components across all 7 automotive EV pillars, executes deterministic technical and diagnostic evaluations, determines grounded circular pathways (REUSE, REFURBISH, RECYCLE, or ASSESSMENT REQUIRED), and on-demand synthesizes mathematically grounded Standard Operating Procedures (SOPs) based on real diagnostic telemetry, environmental carbon abatement, and economic viability.

---

## 🌟 Core Architecture & Capabilities

### 1. Universal 7-Pillar Automotive Architecture
CogniCycle EV evaluates components across the entire electric powertrain and vehicle ecosystem:
1. **High-Voltage Battery & Energy Storage:** Traction battery packs, modules, cylindrical/prismatic cells, and Battery Management Systems (BMS).
2. **Electric Drive & Traction Motors:** Permanent magnet synchronous motors (PMSM), AC induction motors, rotors, stators, and high-speed bearings.
3. **Power Electronics:** Silicon/SiC traction inverters, bi-directional DC-DC converters, IGBT modules, high-voltage busbars, and DC link capacitors.
4. **Charging Electronics:** On-board chargers (OBC), fast-charging communication controllers, high-voltage relays, and pyrofuses.
5. **Control & Computing:** Gateway ECUs, Vehicle Control Units (VCUs), body controllers, and autonomous drive compute modules.
6. **Sensors & Communication:** Current/voltage sensors, ADAS radar sensors, camera modules, ultrasonic sensors, and CAN-FD transceivers.
7. **Auxiliary Electronics:** Electric A/C compressors, thermal management heat pumps, electric power steering (EPS) actuators, and infotainment clusters.

### 2. Grounded Telemetry & Diagnostic Decision Engine
- **Accurate Inferences:** Components with high State of Health (SOH ≥ 80%) and normal telemetry are accurately assigned to high-value **REUSE** (e.g. secondary commercial stationary BESS or vehicle spares).
- **Distinguishing Voltage from Risk:** Standard EV high voltage (`high_voltage: true`) is treated with appropriate handling protocols, while genuine hazards (thermal runaway history, enclosure punctures) are quarantined and routed to closed-loop recycling.
- **Realistic Automotive Specifications:** All 105 benchmark components feature verified real-world weights in kilograms (e.g., 28 kg for battery modules, 450 kg for complete packs, 16 kg for inverters, 65 kg for traction motors) and verified secondary market valuations.

### 3. Interactive Decision Engine Rationale ("Lighten" Action)
- Every disposition badge (**REUSE**, **REFURBISH**, **RECYCLE**, **ASSESSMENT REQUIRED**) across the table and dashboard functions as an interactive button.
- Clicking any disposition badge opens the **Decision Engine Rationale Dialog**:
  - Exact diagnostic telemetry (SOH %, cycle counts, impedance).
  - Safety and enclosure screening status.
  - Techno-economic justification (gross value vs repair/testing costs).
  - Quantitative carbon abatement and critical raw material conservation.

### 4. On-Demand Grounded Engineering Protocols (SOPs)
- **Token-Optimized Model Integration:** When clicking **"Take Action"**, the system generates a concise, 5-step Standard Operating Procedure using Groq LLM with strictly filtered telemetry context to minimize token usage.
- **Persistent Caching:** Generated protocols are archived in `backend/data/output/action_plans.json` keyed by `asset_id`. Subsequent clicks load immediately from cache with zero latency.
- **Enterprise Standards:** Clean, professional UI free of developer debugging statements or gimmick text.

### 5. Custom Dataset Ingestion
- Upload custom JSON datasets directly from the frontend dropzone.
- Automatic schema validation, 7-pillar routing, and batch circular disposition assignment.

---

## 📋 Prerequisites

1. **Python 3.10+** (Python 3.12 recommended)
2. **Node.js 18+** & **npm**
3. **Groq API Key** (from [console.groq.com](https://console.groq.com))

---

## 🚀 How to Run the Project Manually

You will need **two terminal windows**:

### Terminal 1: Backend (FastAPI)
```powershell
cd CogniCycle_EV\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Documentation (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Terminal 2: Frontend (React + Vite)
```powershell
cd CogniCycle_EV\frontend
npm.cmd run dev
```
- Web Application: **[http://localhost:5173](http://localhost:5173)**

---

## 🧪 Running Automated Tests
```powershell
cd CogniCycle_EV\backend
python -m pytest
```
All unit tests verify Asset schemas, universal triage agents, triage services, and API endpoints.

---

## 📂 Project Structure
```
CogniCycle_EV/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── universal_triage_agent.py   # 7-Pillar EV subsystem evaluation agent
│   │   │   ├── action_plan_agent.py        # Token-optimized grounded SOP generator
│   │   │   └── battery_agent.py            # Backward-compatibility alias
│   │   ├── api/routes/                     # FastAPI REST API endpoints
│   │   ├── schemas/                        # Pydantic data models
│   │   └── services/
│   │       ├── universal_triage_service.py # Domain triage service
│   │       ├── routing_service.py          # 7-pillar classification router
│   │       ├── decision_engine.py          # Grounded circular disposition logic
│   │       ├── pipeline_service.py         # End-to-end evaluation orchestrator
│   │       ├── storage_service.py          # Persistent cache storage
│   │       └── action_plan_service.py      # SOP protocol caching & dispatch
│   ├── data/
│   │   ├── input/assets.json               # 105 benchmark components with realistic specs
│   │   └── output/                         # Cached triage and action plan outputs
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── navigation/                 # Modern sticky navbar
│   │   │   ├── views/                      # Overview, TriageExplorer, UploadView, ActionPlans, Analytics
│   │   │   ├── modals/                     # ActionPlanModal, AssetDetailModal, DispositionRationaleModal
│   │   │   └── dashboard/                  # Central state controller
│   │   ├── App.jsx
│   │   └── index.css                       # Enterprise design system
```
