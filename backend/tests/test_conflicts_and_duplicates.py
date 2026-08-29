from app.services.duplicates_conflicts import duplicate_detector, conflict_engine

def test_duplicate_similarity():
    sim = duplicate_detector.calculate_similarity("Ramesh Kumar Sharma", "Ramesh K. Sharma")
    assert sim >= 0.85

def test_conflict_engine_detection():
    records = [
        {"id": 1, "document_title": "Jamabandi.pdf", "khasra_number": "245/1", "owner_name": "Ramesh Kumar Sharma", "land_area": 4.25, "village": "Rampur"},
        {"id": 2, "document_title": "SaleDeed.png", "khasra_number": "245/1", "owner_name": "Suresh Kumar Verma", "land_area": 4.10, "village": "Rampur"}
    ]
    
    res = conflict_engine.detect_conflicts("245/1", "Rampur", records)
    assert len(res["conflicts"]) >= 1
    assert res["graph_payload"]["nodes"] is not None
