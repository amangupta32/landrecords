# AI-Powered Intelligent Land Record Digitization and Validation System

> **DEMO DATA — NOT AN OFFICIAL LAND RECORD**  
> All external system integrations (LRMS, DILRMP, Aadhaar, Registration databases) are implemented using an integration-ready Adapter pattern for demonstration purposes.

## System Highlights
- **Document Preprocessing**: OpenCV-based grayscale conversion, noise reduction, CLAHE contrast enhancement, Hough Transform deskewing, Otsu thresholding, and Laplacian blur quality scoring.
- **Modular OCR Engine Abstraction**: Support for Tesseract, PaddleOCR, Indic HTR, and a robust offline Land Record Fallback engine.
- **Hybrid NLP Field Extractor**: Regex, context window rules, and proximity heuristics to extract Owner Names, Khasra/Survey Numbers, Khata Numbers, Land Area, Location hierarchy (Village -> Tehsil -> District -> State), Mutation References, and Record Dates.
- **Multi-Level Explainable Confidence Engine**: 4-tiered scoring model ($\text{OCR} \times 0.40 + \text{Extraction} \times 0.30 + \text{Validation} \times 0.20 + \text{Context} \times 0.10$) with human-readable rationale explanations.
- **Rule & Location Hierarchy Validation Engine**: Formats, mandatory fields, non-zero land areas, unit conversions (Acres/Hectares/Bigha -> SQ meters), and administrative hierarchy checks.
- **Duplicate & Cross-Document Conflict Graph Engine**: Levenshtein fuzzy matching and cross-document relational graph linking Jamabandi, Mutations, and Deeds for identical Khasra plots.
- **Human-in-the-Loop Split-Screen Workstation**: Interactive document viewer with overlay bounding box sync, inline editor, explainability modals, and single-click approval/rejection.
- **GIS Cadastral Map**: Leaflet interactive map displaying village land plots color-coded by verification and conflict status.
- **AI Research Experiments Bench**: Automated benchmark suite (`scripts/run_experiments.py`) testing CER, WER, extraction F1-scores, and latency.

## Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.database.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Running Benchmark Research Experiments
```bash
python scripts/run_experiments.py
```

### Running Backend Unit & Integration Tests
```bash
cd backend
pytest tests/
```
