from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.session import get_db
from app.models.domain import DuplicateCandidate, LandRecord, AuditLog

router = APIRouter(prefix="/duplicates", tags=["Duplicates"])

class ResolveDuplicateRequest(BaseModel):
    action: str  # MERGE, DISMISS
    primary_record_id: int

@router.get("")
def list_duplicates(db: Session = Depends(get_db)):
    dups = db.query(DuplicateCandidate).order_by(DuplicateCandidate.id.desc()).all()
    return dups

@router.post("/{dup_id}/resolve")
def resolve_duplicate(dup_id: int, req: ResolveDuplicateRequest, db: Session = Depends(get_db)):
    dup = db.query(DuplicateCandidate).filter(DuplicateCandidate.id == dup_id).first()
    if not dup:
        raise HTTPException(status_code=404, detail="Duplicate record not found")

    if req.action.upper() == "MERGE":
        dup.status = "Merged"
        # Update primary record
        primary = db.query(LandRecord).filter(LandRecord.id == req.primary_record_id).first()
        if primary:
            primary.verification_status = "Verified"
    else:
        dup.status = "Dismissed"

    db.commit()

    db.add(AuditLog(
        user_name="Ananya Verma",
        user_role="Verifier",
        action=f"DUPLICATE_{req.action.upper()}",
        target_type="DUPLICATE_CANDIDATE",
        target_id=str(dup_id),
        details={"status": dup.status, "primary_id": req.primary_record_id}
    ))
    db.commit()

    return {"message": f"Duplicate resolution '{req.action}' completed successfully."}
