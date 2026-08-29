from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database.session import get_db
from app.models.domain import LandRecord, LandRecordField, ValidationResult

router = APIRouter(prefix="/land-records", tags=["Land Records"])

@router.get("")
def search_land_records(
    search: Optional[str] = None,
    status: Optional[str] = None,
    village: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LandRecord)
    
    if status:
        query = query.filter(LandRecord.verification_status == status)
    if village:
        query = query.filter(LandRecord.village == village)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (LandRecord.owner_name.ilike(search_pattern)) |
            (LandRecord.khasra_number.ilike(search_pattern)) |
            (LandRecord.village.ilike(search_pattern))
        )
        
    records = query.order_by(LandRecord.id.desc()).all()
    return records

@router.get("/{record_id}")
def get_land_record_detail(record_id: int, db: Session = Depends(get_db)):
    record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Land record not found")
    
    fields = db.query(LandRecordField).filter(LandRecordField.land_record_id == record_id).all()
    validations = db.query(ValidationResult).filter(ValidationResult.land_record_id == record_id).all()

    return {
        "record": record,
        "fields": fields,
        "validations": validations
    }
