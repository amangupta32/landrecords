from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="Verifier")  # Admin, Verifier, Data Entry Operator, Supervisor, Viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    preprocessed_path = Column(String, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Uploaded")  # Uploaded, Preprocessing, OCR, FieldExtraction, Validation, Complete, Error
    
    # Document Quality Assessment Metrics
    quality_score = Column(Float, default=0.0)
    blur_metric = Column(Float, default=0.0)  # Laplacian variance
    contrast_metric = Column(Float, default=0.0)
    skew_angle = Column(Float, default=0.0)
    noise_level = Column(String, default="Low")  # Low, Medium, High

    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    ocr_results = relationship("OCRResult", back_populates="document", cascade="all, delete-orphan")
    land_records = relationship("LandRecord", back_populates="document", cascade="all, delete-orphan")

class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    image_path = Column(String, nullable=False)

    document = relationship("Document", back_populates="pages")

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    engine_name = Column(String, nullable=False)  # Tesseract, PaddleOCR, IndicHTR, Fallback
    detected_language = Column(String, default="Hindi/English")
    full_text = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=True)
    word_boxes = Column(JSON, nullable=True)  # List of {text, bbox, confidence, page}
    line_boxes = Column(JSON, nullable=True)
    base_ocr_confidence = Column(Float, default=0.0)

    document = relationship("Document", back_populates="ocr_results")

class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    document_type = Column(String, default="Jamabandi / ROR")  # Jamabandi, Sale Deed, Mutation Record, Khasra Girdawari
    
    # Core Fields
    khasra_number = Column(String, index=True, nullable=True)
    khata_number = Column(String, index=True, nullable=True)
    survey_number = Column(String, index=True, nullable=True)
    owner_name = Column(String, index=True, nullable=True)
    owner_father_name = Column(String, nullable=True)
    land_area = Column(Float, nullable=True)
    land_area_unit = Column(String, default="Acres")
    area_sq_meters = Column(Float, nullable=True)
    
    # Location Hierarchy
    village = Column(String, index=True, nullable=True)
    tehsil = Column(String, index=True, nullable=True)
    district = Column(String, index=True, nullable=True)
    state = Column(String, index=True, nullable=True)
    
    # Supplementary Metadata
    land_classification = Column(String, nullable=True)
    mutation_ref = Column(String, nullable=True)
    registration_ref = Column(String, nullable=True)
    record_date = Column(String, nullable=True)
    
    # Verification & Confidence
    verification_status = Column(String, default="Pending")  # Pending, Verified, Rejected, LowConfidence, Flagged
    overall_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    document = relationship("Document", back_populates="land_records")
    fields = relationship("LandRecordField", back_populates="land_record", cascade="all, delete-orphan")
    validations = relationship("ValidationResult", back_populates="land_record", cascade="all, delete-orphan")

class LandRecordField(Base):
    __tablename__ = "land_record_fields"

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey("land_records.id"), nullable=False)
    field_name = Column(String, nullable=False)  # owner_name, khasra_number, khata_number, etc.
    extracted_value = Column(Text, nullable=True)
    source_snippet = Column(Text, nullable=True)
    page_number = Column(Integer, default=1)
    bounding_box = Column(JSON, nullable=True)  # [x, y, w, h] normalized 0-100 or px
    
    # 4-Level Explainable Confidence Breakdown
    ocr_confidence = Column(Float, default=0.0)
    extraction_confidence = Column(Float, default=0.0)
    validation_confidence = Column(Float, default=0.0)
    context_confidence = Column(Float, default=0.0)
    final_confidence = Column(Float, default=0.0)
    confidence_explanation = Column(Text, nullable=True)
    
    # Verifier Overrides
    is_edited = Column(Boolean, default=False)
    edited_value = Column(Text, nullable=True)
    verifier_name = Column(String, nullable=True)

    land_record = relationship("LandRecord", back_populates="fields")

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey("land_records.id"), nullable=False)
    rule_name = Column(String, nullable=False)
    field_name = Column(String, nullable=False)
    is_valid = Column(Boolean, default=True)
    severity = Column(String, default="Error")  # Error, Warning, Info
    message = Column(Text, nullable=False)

    land_record = relationship("LandRecord", back_populates="validations")

class VerificationTask(Base):
    __tablename__ = "verification_tasks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    land_record_id = Column(Integer, ForeignKey("land_records.id"), nullable=False)
    assigned_to_role = Column(String, default="Verifier")
    status = Column(String, default="Pending")  # Pending, InProgress, Completed
    priority = Column(String, default="Medium")  # High, Medium, Low
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    user_role = Column(String, nullable=False)
    action = Column(String, nullable=False)  # UPLOAD, VERIFY, EDIT, REJECT, MERGE, FLAG
    target_type = Column(String, nullable=False)  # DOCUMENT, RECORD, CONFLICT
    target_id = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DuplicateCandidate(Base):
    __tablename__ = "duplicate_candidates"

    id = Column(Integer, primary_key=True, index=True)
    record_id_1 = Column(Integer, nullable=False)
    record_id_2 = Column(Integer, nullable=False)
    owner_1 = Column(String, nullable=False)
    owner_2 = Column(String, nullable=False)
    khasra_number = Column(String, nullable=False)
    village = Column(String, nullable=False)
    similarity_score = Column(Float, nullable=False)
    duplicate_reason = Column(String, nullable=False)
    status = Column(String, default="Pending")  # Pending, Merged, Dismissed
    detected_at = Column(DateTime, default=datetime.utcnow)

class ConflictRecord(Base):
    __tablename__ = "conflict_records"

    id = Column(Integer, primary_key=True, index=True)
    khasra_number = Column(String, index=True, nullable=False)
    village = Column(String, index=True, nullable=False)
    doc_1_title = Column(String, nullable=False)
    doc_2_title = Column(String, nullable=False)
    conflict_type = Column(String, nullable=False)  # Ownership Mismatch, Area Discrepancy, Date Overlap
    description = Column(Text, nullable=False)
    severity = Column(String, default="High")  # Critical, High, Medium
    status = Column(String, default="Active")  # Active, Resolved, Ignored
    detected_at = Column(DateTime, default=datetime.utcnow)

class TrainingFeedback(Base):
    __tablename__ = "training_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)
    field_name = Column(String, nullable=False)
    original_value = Column(Text, nullable=True)
    corrected_value = Column(Text, nullable=False)
    source_region = Column(JSON, nullable=True)
    verifier_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MapFeature(Base):
    __tablename__ = "map_features"

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey("land_records.id"), nullable=True)
    khasra_number = Column(String, index=True, nullable=False)
    village = Column(String, index=True, nullable=False)
    tehsil = Column(String, nullable=False)
    district = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    land_area_acres = Column(Float, nullable=False)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    status = Column(String, default="Verified")  # Verified, LowConfidence, Conflict, Pending
    geometry_geojson = Column(JSON, nullable=False)
