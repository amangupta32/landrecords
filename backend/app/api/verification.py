from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database.session import get_db
from app.models.domain import LandRecord, LandRecordField, AuditLog, Document, TrainingFeedback
from app.services.feedback import feedback_store

router = APIRouter(prefix="/verification", tags=["Verification"])

class VerificationActionRequest(BaseModel):
    action: str  # APPROVE, EDIT, REJECT, FLAG
    verifier_name: str = "Ananya Verma"
    remarks: Optional[str] = None
    edited_fields: Optional[dict] = None  # {field_name: new_value}

@router.get("/queue")
def get_verification_queue(db: Session = Depends(get_db)):
    records = db.query(LandRecord).order_by(LandRecord.overall_confidence.asc()).all()
    queue = []
    for r in records:
        doc = db.query(Document).filter(Document.id == r.document_id).first()
        queue.append({
            "id": r.id,
            "document_id": r.document_id,
            "document_title": doc.filename if doc else "Document.pdf",
            "khasra_number": r.khasra_number,
            "owner_name": r.owner_name,
            "village": r.village,
            "verification_status": r.verification_status,
            "overall_confidence": r.overall_confidence,
            "priority": "High" if r.overall_confidence < 0.7 else ("Medium" if r.verification_status == "Flagged" else "Normal")
        })
    return queue

@router.post("/{record_id}/action")
def submit_verification_action(record_id: int, req: VerificationActionRequest, db: Session = Depends(get_db)):
    record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Land record not found")

    action_upper = req.action.upper()

    if action_upper == "APPROVE":
        record.verification_status = "Verified"
    elif action_upper == "REJECT":
        record.verification_status = "Rejected"
    elif action_upper == "FLAG":
        record.verification_status = "Flagged"
    elif action_upper == "EDIT":
        record.verification_status = "Verified"
        if req.edited_fields:
            for field_name, new_val in req.edited_fields.items():
                f_model = db.query(LandRecordField).filter(
                    LandRecordField.land_record_id == record_id,
                    LandRecordField.field_name == field_name
                ).first()
                if f_model:
                    old_val = f_model.extracted_value
                    f_model.is_edited = True
                    f_model.edited_value = str(new_val)
                    f_model.extracted_value = str(new_val)
                    f_model.final_confidence = 1.00
                    f_model.confidence_explanation = f"Manually verified & corrected by {req.verifier_name}."
                    
                    # Update top level record field if applicable
                    if hasattr(record, field_name):
                        setattr(record, field_name, new_val)

                    # Log to continuous learning feedback store
                    feedback_store.record_feedback(
                        db=db,
                        document_id=record.document_id,
                        field_name=field_name,
                        original_val=old_val,
                        corrected_val=str(new_val),
                        source_region=f_model.bounding_box,
                        verifier_name=req.verifier_name
                    )

    db.commit()

    # Log Audit Action
    db.add(AuditLog(
        user_name=req.verifier_name,
        user_role="Verifier",
        action=action_upper,
        target_type="LAND_RECORD",
        target_id=str(record_id),
        details={"remarks": req.remarks, "status": record.verification_status}
    ))
    db.commit()

    return {
        "record_id": record_id,
        "status": record.verification_status,
        "message": f"Verification action '{action_upper}' processed successfully."
    }
