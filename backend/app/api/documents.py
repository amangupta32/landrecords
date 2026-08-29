from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
from typing import List

from app.database.session import get_db
from app.models.domain import Document, LandRecord, LandRecordField, ValidationResult, AuditLog
from app.services.preprocessing import preprocessor
from app.services.ocr import OCRManager
from app.services.extraction import field_extractor
from app.services.confidence import confidence_engine
from app.services.validation import validation_engine
from app.core.config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])

def run_document_processing_pipeline(doc_id: int, db_session_factory):
    db = db_session_factory()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return

        doc.status = "Preprocessing"
        db.commit()

        # Step 1: OpenCV Image Preprocessing
        prep_path = doc.file_path.replace(".", "_prep.")
        metrics = preprocessor.process_image(doc.file_path, prep_path)
        doc.preprocessed_path = prep_path
        doc.quality_score = metrics["quality_score"]
        doc.blur_metric = metrics["blur_metric"]
        doc.contrast_metric = metrics["contrast_metric"]
        doc.skew_angle = metrics["skew_angle"]
        doc.noise_level = metrics["noise_level"]

        # Step 2: OCR Text & Bounding Box Extraction
        doc.status = "OCR"
        db.commit()
        ocr_provider = OCRManager.get_provider(settings.DEFAULT_OCR_ENGINE)
        ocr_data = ocr_provider.extract_text_and_boxes(doc.file_path)

        # Step 3: Hybrid NLP Field Extraction
        doc.status = "FieldExtraction"
        db.commit()
        extracted_fields = field_extractor.extract_fields(
            full_text=ocr_data["full_text"],
            normalized_text=ocr_data["normalized_text"],
            word_boxes=ocr_data["word_boxes"]
        )

        # Step 4: Validation Engine
        doc.status = "Validation"
        db.commit()
        flat_record = {
            "owner_name": extracted_fields["owner_name"]["value"],
            "khasra_number": extracted_fields["khasra_number"]["value"],
            "land_area": extracted_fields["land_area"]["value"],
            "land_area_unit": extracted_fields["land_area"]["unit"],
            "village": extracted_fields["village"]["value"],
            "tehsil": extracted_fields["tehsil"]["value"],
            "district": extracted_fields["district"]["value"],
            "state": extracted_fields["state"]["value"]
        }
        val_res = validation_engine.validate_record(flat_record)

        # Step 5: Save Land Record & Multi-level Explainable Fields
        land_rec = LandRecord(
            document_id=doc.id,
            document_type="Scanned Land Document",
            khasra_number=flat_record["khasra_number"],
            khata_number=extracted_fields["khata_number"]["value"],
            owner_name=flat_record["owner_name"],
            land_area=flat_record["land_area"],
            land_area_unit=flat_record["land_area_unit"],
            area_sq_meters=val_res["area_sq_meters"],
            village=flat_record["village"],
            tehsil=flat_record["tehsil"],
            district=flat_record["district"],
            state=flat_record["state"],
            mutation_ref=extracted_fields["mutation_ref"]["value"],
            record_date=extracted_fields["record_date"]["value"],
            verification_status="Pending",
            overall_confidence=0.88
        )
        db.add(land_rec)
        db.commit()
        db.refresh(land_rec)

        # Save Fields with Confidence & Rationale
        field_models = []
        conf_scores = []
        for key, info in extracted_fields.items():
            conf_data = confidence_engine.compute_field_confidence(
                field_name=key,
                ocr_conf=ocr_data["base_ocr_confidence"],
                extraction_conf=info["extraction_confidence"],
                validation_conf=1.0 if val_res["overall_valid"] else 0.7,
                context_conf=0.90
            )
            conf_scores.append(conf_data["final_confidence"])

            field_models.append(LandRecordField(
                land_record_id=land_rec.id,
                field_name=key,
                extracted_value=str(info.get("formatted", info.get("value", ""))),
                source_snippet=info.get("source_snippet", ""),
                bounding_box=info.get("bbox", [100, 100, 100, 30]),
                ocr_confidence=conf_data["ocr_confidence"],
                extraction_confidence=conf_data["extraction_confidence"],
                validation_confidence=conf_data["validation_confidence"],
                context_confidence=conf_data["context_confidence"],
                final_confidence=conf_data["final_confidence"],
                confidence_explanation=conf_data["confidence_explanation"]
            ))

        db.add_all(field_models)
        
        # Save Validation Results
        for v in val_res["validations"]:
            db.add(ValidationResult(
                land_record_id=land_rec.id,
                rule_name=v["rule_name"],
                field_name=v["field_name"],
                is_valid=v["is_valid"],
                severity=v["severity"],
                message=v["message"]
            ))

        # Update overall confidence
        land_rec.overall_confidence = round(sum(conf_scores) / len(conf_scores), 2) if conf_scores else 0.85
        if land_rec.overall_confidence < settings.CONFIDENCE_MEDIUM_THRESHOLD:
            land_rec.verification_status = "LowConfidence"

        doc.status = "Complete"
        db.commit()

        # Audit Log
        db.add(AuditLog(
            user_name="AI Pipeline",
            user_role="System",
            action="PROCESS_COMPLETE",
            target_type="DOCUMENT",
            target_id=str(doc.id),
            details={"confidence": land_rec.overall_confidence, "quality": doc.quality_score}
        ))
        db.commit()
    except Exception as e:
        db.rollback()
        doc.status = "Error"
        db.commit()
    finally:
        db.close()

@router.post("/upload")
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(settings.STORAGE_PATH, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = Document(
        filename=file.filename,
        original_name=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        file_size=os.path.getsize(file_path),
        file_path=file_path,
        status="Uploaded"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Trigger Async AI Processing Pipeline
    from app.database.session import SessionLocal
    background_tasks.add_task(run_document_processing_pipeline, doc.id, SessionLocal)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "message": "File uploaded successfully. AI processing pipeline started."
    }

@router.get("")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return docs

@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
