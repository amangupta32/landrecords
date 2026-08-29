from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_dashboard_stats():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "confidence_distribution" in data

def test_gis_map_features():
    response = client.get("/api/gis/map-features?village=Rampur")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"

def test_list_land_records():
    response = client.get("/api/land-records")
    assert response.status_code == 200
    records = response.json()
    assert len(records) > 0

def test_experiments_run():
    response = client.get("/api/experiments/run")
    assert response.status_code == 200
    data = response.json()
    assert "ocr_engine_comparison" in data
