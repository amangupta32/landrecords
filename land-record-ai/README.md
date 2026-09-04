# Land Record AI (`land-record-ai`)

Modular, production-ready AI pipeline for document preprocessing, multi-engine OCR, hybrid NLP field extraction, geographic validation, and explainable confidence scoring for Indian land records (Khasra, Khata, Jamabandi, Mutation, Registry).

## Architecture

```text
DOCUMENT (PDF/JPG/PNG/TIFF)
  │
  ▼
Document Quality Analysis (Laplacian Blur, Contrast, Brightness, DPI)
  │
  ▼
OpenCV Preprocessing Pipeline (Grayscale, Denoise, CLAHE, Deskew, Otsu)
  │
  ▼
OCR Engine Router (Tesseract, PaddleOCR, Indic HTR, Fallback)
  │
  ▼
OCR Normalization (Indic Numerals ०-९ → 0-9, Punctuation, Bounding Boxes)
  │
  ▼
Hybrid NLP Field Extraction (Regex, Multi-Lingual Owner & Relationships, Location Hierarchy, Context Windows)
  │
  ▼
Validation Engine (Format, Geographic Hierarchy, Cross-field, Area SI Conversions)
  │
  ▼
Explainable Confidence Engine (OCR × 0.40 + Extraction × 0.30 + Validation × 0.20 + Context × 0.10)
  │
  ▼
Structured Canonical JSON Output & Human Review Routing
```

## Milestone Status

- [x] **Milestone 1**: Complete folder layout, Pydantic Schemas, YAML configuration suite, independent OpenCV Preprocessing pipeline, Laplacian quality analysis, unit testing.
- [x] **Milestone 2**: OCR Abstraction, Tesseract, PaddleOCR, Indic HTR, Normalization.
- [x] **Milestone 3**: Indic numeral normalization, Regex extraction (Khasra, Khata, Area, Date).
- [x] **Milestone 4**: Owner extraction, Location hierarchy (Village->Tehsil->District->State), Mutation references.
- [x] **Milestone 5**: Context windows, Proximity scoring, Candidate ranking.
- [x] **Milestone 6**: Validation, Geographic hierarchy validation, Cross-field consistency.
- [x] **Milestone 7**: Explainable confidence scoring, Tiers, Human-readable explanations.
- [x] **Milestone 8**: OCR routing, OCR ensemble, Offline land record fallback.
- [x] **Milestone 9**: Evaluation framework (CER, WER, F1), Benchmarking, FastAPI endpoints.

## Running Tests

```bash
cd land-record-ai
pytest tests/ -v
```

## Running the End-to-End Demo

```bash
python land-record-ai/demo.py
```

## Running the FastAPI AI Service

```bash
uvicorn api.main:app --reload --port 8001
```
