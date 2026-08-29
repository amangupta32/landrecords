from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import ConflictRecord, LandRecord
from app.services.duplicates_conflicts import conflict_engine

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])

@router.get("")
def list_conflicts(db: Session = Depends(get_db)):
    conflicts = db.query(ConflictRecord).order_by(ConflictRecord.id.desc()).all()
    return conflicts

@router.get("/graph/{khasra_number}")
def get_conflict_graph(khasra_number: str, village: str = "Rampur", db: Session = Depends(get_db)):
    records = db.query(LandRecord).filter(LandRecord.village == village).all()
    rec_dicts = [
        {
            "id": r.id,
            "document_title": r.document_type,
            "khasra_number": r.khasra_number,
            "owner_name": r.owner_name,
            "land_area": r.land_area,
            "village": r.village
        }
        for r in records
    ]
    graph_res = conflict_engine.detect_conflicts(khasra_number, village, rec_dicts)
    return graph_res
