"""Unit tests for FastAPI endpoints."""

import io
import cv2
from fastapi.testclient import TestClient
import numpy as np
import pytest
from PIL import Image

from api.main import app

client = TestClient(app)


def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_api_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "fallback" in data["available_ocr_engines"]


def test_api_process_document():
    # Create test image in memory
    img = np.full((300, 400, 3), 255, dtype=np.uint8)
    cv2.putText(img, "TEST", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    is_success, buffer = cv2.imencode(".png", img)
    assert is_success

    files = {"file": ("test_doc.png", io.BytesIO(buffer), "image/png")}
    response = client.post("/api/v1/process", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "test_doc"
    assert "fields" in data
    assert "confidence" in data
    assert "field_confidences" in data
    assert "document_quality" in data


def test_api_validate():
    payload = {
        "owner_names": [{"name": "Ramesh Kumar Sharma", "relation_type": "S/O", "relation_name": "Harish Chandra"}],
        "khasra_numbers": [{"value": "245/1"}],
        "khata_numbers": [{"value": "89"}],
        "land_area": {"value": 4.25, "unit": "acre"},
        "location": {"village": "Rampur", "tehsil": "Rampur Tehsil", "district": "Rampur District", "state": "Uttar Pradesh"}
    }
    response = client.post("/api/v1/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["validation_score"] >= 0.8
