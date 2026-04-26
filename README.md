# Veritas — Truth Layer for Indian Healthcare

> AI-powered verification system that detects false healthcare facility claims and identifies medical deserts using multi-agent debate.

[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com)
[![Databricks](https://img.shields.io/badge/Platform-Databricks-FF3621)](https://databricks.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Overview

India has 10,000+ healthcare facilities with **self-reported, unverified capability claims**. A hospital might claim "24/7 emergency surgery" while their notes reveal "limited weekend staff."

**Veritas** solves this by:
- Running a **3-agent AI debate** (Advocate, Skeptic, Judge) on each facility
- Detecting **contradictions** between claims and evidence
- Generating **explainable trust scores** (0-100)
- Mapping **medical deserts** where critical care is inaccessible

**Built for:** State Health Departments, Policymakers, Healthcare NGOs, Hospital Networks

---

## Key Features

### Multi-Agent Trust Debate
Three AI agents argue over each facility's claims:
- **Advocate:** Presents evidence supporting the facility
- **Skeptic:** Hunts for contradictions, gaps, and unverified claims
- **Judge:** Weighs arguments and assigns an explainable score

### Contradiction Detection
Automatically flags inconsistencies like:
> "Oncology center available" ↔ "Oncology department under construction"

We found **56 critical contradictions** across 10,000 facilities.

### Medical Desert Mapping
Interactive map showing regions by distance to verified critical care:
- 🟢 Green: <50km
- 🟡 Yellow: 50-100km
- 🔴 Red: >100km (medical desert)

### Natural Language Query
Ask questions like:
- "Hospitals in Bihar with low trust scores"
- "Dialysis facilities in Maharashtra"

### Full Traceability
Every trust score links to the complete debate transcript — see exactly why a facility scored 62 instead of 85.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATABRICKS PLATFORM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │ Stage 1  │ → │ Stage 2  │ → │ Stage 3  │ → │ Stage 4  │      │
│  │Ingestion │   │Extraction│   │  Trust   │   │Geographic│      │
│  │          │   │          │   │  Debate  │   │          │      │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘      │
│       │              │              │              │             │
│       ▼              ▼              ▼              ▼             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    DELTA LAKE                            │    │
│  │  facilities_raw | facilities_structured | trust_scores   │    │
│  │  contradictions | geo_lookup | facility_embeddings       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    MLFLOW TRACING                        │    │
│  │            Every LLM call is auditable                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────┐                      ┌─────────────┐          │
│   │   FastAPI   │  ←── REST API ──→    │  Streamlit  │          │
│   │   (Vercel)  │                      │   (Cloud)   │          │
│   └─────────────┘                      └─────────────┘          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

### Stage 1: Ingestion
Loads raw facility data from Excel into Delta Lake with schema validation.

### Stage 2: Extraction
LLM extracts structured data from unstructured notes:
- Verified capabilities (with confidence scores)
- Staff information
- Equipment inventory

### Stage 3: Trust Debate
The core innovation — three agents debate each facility:
```
Advocate: "AIIMS Patna has 750 beds with emergency surgery available..."
Skeptic:  "WAIT — notes say 'limited staff on weekends.' -15 points."
Judge:    "Valid concern. Score: 62/100. Use for weekday emergencies only."
```

### Stage 4: Geographic
Calculates Haversine distances to identify medical deserts:
- Finds nearest facility for each capability
- Classifies regions by accessibility (green/yellow/red)

### Stage 5: Vector Index
Creates BGE-Large embeddings for semantic facility search.

---

## Tech Stack

**Platform:** Databricks (Delta Lake, Unity Catalog, Model Serving)

**AI Models:**
- Llama 3.3 70B — Multi-agent trust debate
- BGE-Large-EN — Semantic embeddings (1024 dimensions)

**Observability:** MLflow Tracing

**Backend:** FastAPI (deployed on Vercel)

**Frontend:** Streamlit with Folium maps (deployed on Streamlit Cloud)

**Languages:** Python 3.12

---

## Project Structure

```
veritas/
├── api/                    # FastAPI backend
│   ├── main.py            # Application entry point
│   ├── mock_data.py       # Sample data for local development
│   ├── llm_client.py      # Databricks LLM client
│   ├── routers/           # API endpoints
│   │   ├── facilities.py  # /api/facilities
│   │   ├── trust.py       # /api/trust
│   │   ├── maps.py        # /api/map
│   │   ├── query.py       # /api/query
│   │   └── health.py      # /api/health
│   └── schemas/           # Pydantic models
│
├── frontend/              # Streamlit frontend
│   ├── app.py            # Main application
│   └── tabs/             # UI components
│       ├── map_tab.py    # Geographic explorer
│       ├── inspector_tab.py  # Facility details
│       └── query_tab.py  # Natural language search
│
├── pipelines/             # Databricks notebooks (.py.databricks)
│   ├── ingestion.py      # Stage 1
│   ├── extraction.py     # Stage 2
│   ├── trust_debate.py   # Stage 3
│   ├── geographic.py     # Stage 4
│   └── vector_index.py   # Stage 5
│
├── prompts/               # LLM prompt templates
├── notebooks/             # Databricks notebook versions
├── requirements.txt       # API dependencies (minimal)
├── requirements-full.txt  # Full dependencies
└── vercel.json           # Vercel deployment config
```

---

## Quick Start

### Local Development (Mock Data)

```bash
# Clone the repository
git clone https://github.com/codebyharshx/veritasai.git
cd veritasai

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn api.main:app --reload

# In another terminal, start the frontend
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

The API automatically uses mock data when running locally (no Databricks required).

### Databricks Deployment

1. Import notebooks from `notebooks/` into Databricks workspace
2. Configure Unity Catalog schema: `workspace.veritas_dev`
3. Run pipelines in order: Stage 1 → 2 → 3 → 4 → 5
4. Deploy API with Databricks connection

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check and table counts |
| `/api/facilities` | GET | List facilities with filters |
| `/api/facilities/{id}` | GET | Facility details with trust score |
| `/api/trust/{id}/debate` | GET | Full debate transcript |
| `/api/trust/stats` | GET | Aggregate trust statistics |
| `/api/map/{capability}` | GET | Medical desert data |
| `/api/query` | POST | Natural language search |

---

## Results

**Quantitative:**
- Processed **10,000** Indian healthcare facilities
- Detected **56** critical contradictions
- Generated trust scores for **9,134** facilities (range: 45-92)
- Identified multiple **medical deserts** (>100km to emergency care)

**Sample Finding:**
> AIIMS Patna claims "emergency surgery available" but notes reveal "limited staff on weekends"
>
> **Trust Score: 62/100** — Use for weekday emergencies only

---

## Team

Built for **Hack-Nation 5th Global AI Hackathon** — Databricks Track

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Databricks for platform access and model serving
- Anthropic Claude for development assistance
- Indian healthcare dataset providers
