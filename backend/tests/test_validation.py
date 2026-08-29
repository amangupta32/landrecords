from app.services.validation import validation_engine

def test_validation_engine_valid_record():
    record = {
        "owner_name": "Ramesh Kumar Sharma",
        "khasra_number": "245/1",
        "land_area": 4.25,
        "land_area_unit": "Acres",
        "village": "Rampur",
        "tehsil": "Rampur Tehsil",
        "district": "Rampur District",
        "state": "Uttar Pradesh"
    }
    
    res = validation_engine.validate_record(record)
    assert res["overall_valid"] is True
    assert res["area_sq_meters"] == round(4.25 * 4046.86, 1)

def test_validation_engine_missing_owner():
    record = {
        "owner_name": "Unknown Owner",
        "khasra_number": "245/1",
        "land_area": 4.25,
        "village": "Rampur"
    }
    
    res = validation_engine.validate_record(record)
    assert res["overall_valid"] is False
