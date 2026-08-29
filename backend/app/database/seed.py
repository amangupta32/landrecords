import os
import sys
from datetime import datetime

# Add parent directory to sys.path so app imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.session import Base, engine, SessionLocal
from app.models.domain import (
    User, Document, DocumentPage, OCRResult, LandRecord, LandRecordField,
    ValidationResult, VerificationTask, AuditLog, DuplicateCandidate,
    ConflictRecord, TrainingFeedback, MapFeature
)
from app.core.security import get_password_hash

def seed_database():
    print("Initializing database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding demo users...")
        users = [
            User(username="admin", email="admin@gov.in", full_name="Rajesh Sharma (Admin)", hashed_password=get_password_hash("admin123"), role="Admin"),
            User(username="verifier", email="verifier@gov.in", full_name="Ananya Verma (Senior Verifier)", hashed_password=get_password_hash("verifier123"), role="Verifier"),
            User(username="operator", email="operator@gov.in", full_name="Sanjay Patel (Data Entry Operator)", hashed_password=get_password_hash("operator123"), role="Data Entry Operator"),
            User(username="supervisor", email="supervisor@gov.in", full_name="Vikram Singh (Tehsildar Supervisor)", hashed_password=get_password_hash("super123"), role="Supervisor"),
            User(username="viewer", email="viewer@gov.in", full_name="Sunita Rao (Public Viewer)", hashed_password=get_password_hash("viewer123"), role="Viewer"),
        ]
        db.add_all(users)
        db.commit()

        print("Seeding sample documents...")
        doc1 = Document(
            filename="jamabandi_rampur_2024.pdf",
            original_name="Jamabandi_2024_Khasra_245.pdf",
            mime_type="application/pdf",
            file_size=2450000,
            file_path="uploads/jamabandi_rampur_2024.pdf",
            preprocessed_path="uploads/jamabandi_rampur_2024_prep.png",
            status="Complete",
            quality_score=0.92,
            blur_metric=310.5,
            contrast_metric=84.2,
            skew_angle=-0.8,
            noise_level="Low"
        )
        doc2 = Document(
            filename="saledeed_2023_992.png",
            original_name="SaleDeed_Khasra_245_Deed.png",
            mime_type="image/png",
            file_size=1850000,
            file_path="uploads/saledeed_2023_992.png",
            preprocessed_path="uploads/saledeed_2023_992_prep.png",
            status="Complete",
            quality_score=0.78,
            blur_metric=180.2,
            contrast_metric=62.1,
            skew_angle=2.4,
            noise_level="Medium"
        )
        doc3 = Document(
            filename="mutation_record_2022.pdf",
            original_name="Mutation_Record_Khasra_118.pdf",
            mime_type="application/pdf",
            file_size=1200000,
            file_path="uploads/mutation_record_2022.pdf",
            preprocessed_path="uploads/mutation_record_2022_prep.png",
            status="Complete",
            quality_score=0.88,
            blur_metric=275.0,
            contrast_metric=79.0,
            skew_angle=0.1,
            noise_level="Low"
        )
        doc4 = Document(
            filename="khasra_girdawari_legacy.png",
            original_name="Legacy_Handwritten_Girdawari_1998.png",
            mime_type="image/png",
            file_size=3100000,
            file_path="uploads/khasra_girdawari_legacy.png",
            preprocessed_path="uploads/khasra_girdawari_legacy_prep.png",
            status="Complete",
            quality_score=0.64,
            blur_metric=95.4,
            contrast_metric=45.3,
            skew_angle=-3.2,
            noise_level="High"
        )

        db.add_all([doc1, doc2, doc3, doc4])
        db.commit()

        print("Seeding sample land records...")
        rec1 = LandRecord(
            document_id=doc1.id,
            document_type="Jamabandi / ROR",
            khasra_number="245/1",
            khata_number="89",
            survey_number="SURV-102",
            owner_name="Ramesh Kumar Sharma",
            owner_father_name="Harish Chandra Sharma",
            land_area=4.25,
            land_area_unit="Acres",
            area_sq_meters=17199.1,
            village="Rampur",
            tehsil="Rampur Tehsil",
            district="Rampur District",
            state="Uttar Pradesh",
            land_classification="Agricultural (Irrigated)",
            mutation_ref="MUT-2023-882",
            registration_ref="REG-UP-9921",
            record_date="2024-01-15",
            verification_status="Verified",
            overall_confidence=0.94
        )

        rec2 = LandRecord(
            document_id=doc2.id,
            document_type="Sale Deed",
            khasra_number="245/1",
            khata_number="89",
            survey_number="SURV-102",
            owner_name="Suresh Kumar Verma",
            owner_father_name="Ram Lal Verma",
            land_area=4.10,
            land_area_unit="Acres",
            area_sq_meters=16592.1,
            village="Rampur",
            tehsil="Rampur Tehsil",
            district="Rampur District",
            state="Uttar Pradesh",
            land_classification="Agricultural",
            mutation_ref="MUT-PENDING",
            registration_ref="REG-UP-9921",
            record_date="2023-11-20",
            verification_status="Flagged",
            overall_confidence=0.72
        )

        rec3 = LandRecord(
            document_id=doc3.id,
            document_type="Mutation Record",
            khasra_number="118",
            khata_number="42",
            survey_number="SURV-054",
            owner_name="Priya Devi",
            owner_father_name="Mahesh Singh",
            land_area=2.50,
            land_area_unit="Hectares",
            area_sq_meters=25000.0,
            village="Chandpur",
            tehsil="Rampur Tehsil",
            district="Rampur District",
            state="Uttar Pradesh",
            land_classification="Residential / Abadi",
            mutation_ref="MUT-2022-104",
            registration_ref="REG-UP-4410",
            record_date="2022-06-10",
            verification_status="Verified",
            overall_confidence=0.91
        )

        rec4 = LandRecord(
            document_id=doc4.id,
            document_type="Khasra Girdawari (Legacy)",
            khasra_number="312/B",
            khata_number="104",
            survey_number="SURV-210",
            owner_name="Ramesh K. Sharma",
            owner_father_name="H. C. Sharma",
            land_area=4.25,
            land_area_unit="Acres",
            area_sq_meters=17199.1,
            village="Rampur",
            tehsil="Rampur Tehsil",
            district="Rampur District",
            state="Uttar Pradesh",
            land_classification="Agricultural",
            mutation_ref="MUT-1998-12",
            registration_ref="REG-UP-1022",
            record_date="1998-04-05",
            verification_status="LowConfidence",
            overall_confidence=0.61
        )

        db.add_all([rec1, rec2, rec3, rec4])
        db.commit()

        print("Seeding fields with 4-level explainable confidence scores...")
        fields = [
            # Fields for Rec 1 (Verified Jamabandi)
            LandRecordField(
                land_record_id=rec1.id,
                field_name="owner_name",
                extracted_value="Ramesh Kumar Sharma",
                source_snippet="खाता धारक का नाम: रमेश कुमार शर्मा पुत्र हरीश चंद्र",
                page_number=1,
                bounding_box=[120, 240, 280, 45],
                ocr_confidence=0.96,
                extraction_confidence=0.95,
                validation_confidence=1.00,
                context_confidence=0.90,
                final_confidence=0.96,
                confidence_explanation="High confidence: Clear printed text match with valid owner entity pattern."
            ),
            LandRecordField(
                land_record_id=rec1.id,
                field_name="khasra_number",
                extracted_value="245/1",
                source_snippet="खसरा संख्या: २४५/१",
                page_number=1,
                bounding_box=[420, 180, 110, 35],
                ocr_confidence=0.98,
                extraction_confidence=0.96,
                validation_confidence=1.00,
                context_confidence=0.95,
                final_confidence=0.97,
                confidence_explanation="High confidence: Precise numeric Devnagari digit normalization."
            ),
            LandRecordField(
                land_record_id=rec1.id,
                field_name="land_area",
                extracted_value="4.25 Acres",
                source_snippet="कुल क्षेत्रफल: ४.२५ एकड़ (१७,१९९.१ वर्ग मीटर)",
                page_number=1,
                bounding_box=[550, 310, 160, 40],
                ocr_confidence=0.92,
                extraction_confidence=0.90,
                validation_confidence=0.95,
                context_confidence=0.90,
                final_confidence=0.92,
                confidence_explanation="High confidence: Area non-zero with standard unit normalization to Sq meters."
            ),
            LandRecordField(
                land_record_id=rec1.id,
                field_name="village",
                extracted_value="Rampur",
                source_snippet="ग्राम: रामपुर, तहसील: रामपुर",
                page_number=1,
                bounding_box=[100, 140, 150, 30],
                ocr_confidence=0.95,
                extraction_confidence=0.95,
                validation_confidence=1.00,
                context_confidence=0.95,
                final_confidence=0.96,
                confidence_explanation="Valid location: Rampur exists under Rampur Tehsil in UP master hierarchy."
            ),

            # Fields for Rec 2 (Flagged Sale Deed)
            LandRecordField(
                land_record_id=rec2.id,
                field_name="owner_name",
                extracted_value="Suresh Kumar Verma",
                source_snippet="क्रेता का नाम: सुरेश कुमार वर्मा",
                page_number=1,
                bounding_box=[140, 260, 260, 42],
                ocr_confidence=0.75,
                extraction_confidence=0.80,
                validation_confidence=0.50,
                context_confidence=0.70,
                final_confidence=0.71,
                confidence_explanation="Attention required: Owner name 'Suresh Kumar Verma' conflicts with registered Jamabandi owner 'Ramesh Kumar Sharma' for Khasra 245/1."
            ),
            LandRecordField(
                land_record_id=rec2.id,
                field_name="land_area",
                extracted_value="4.10 Acres",
                source_snippet="विक्रय क्षेत्रफल: ४.१० एकड़",
                page_number=1,
                bounding_box=[520, 330, 140, 38],
                ocr_confidence=0.82,
                extraction_confidence=0.78,
                validation_confidence=0.70,
                context_confidence=0.65,
                final_confidence=0.75,
                confidence_explanation="Minor area discrepancy: Deed area 4.10 Acres differs slightly from Jamabandi record (4.25 Acres)."
            ),

            # Fields for Rec 4 (Legacy Handwritten Document)
            LandRecordField(
                land_record_id=rec4.id,
                field_name="owner_name",
                extracted_value="Ramesh K. Sharma",
                source_snippet="मालिक: रमेश के. शर्मा",
                page_number=1,
                bounding_box=[110, 290, 210, 50],
                ocr_confidence=0.52,
                extraction_confidence=0.65,
                validation_confidence=0.80,
                context_confidence=0.60,
                final_confidence=0.61,
                confidence_explanation="Low OCR confidence (52%): Legacy handwritten script with character fading."
            )
        ]
        db.add_all(fields)
        db.commit()

        print("Seeding validation rule check results...")
        validations = [
            ValidationResult(land_record_id=rec1.id, rule_name="REQUIRED_FIELDS", field_name="owner_name", is_valid=True, severity="Info", message="All mandatory fields present."),
            ValidationResult(land_record_id=rec1.id, rule_name="AREA_NON_ZERO", field_name="land_area", is_valid=True, severity="Info", message="Land area is positive and valid."),
            ValidationResult(land_record_id=rec1.id, rule_name="LOCATION_HIERARCHY", field_name="village", is_valid=True, severity="Info", message="Village 'Rampur' verified in Tehsil hierarchy."),
            
            ValidationResult(land_record_id=rec2.id, rule_name="CROSS_DOC_OWNERSHIP", field_name="owner_name", is_valid=False, severity="Error", message="Ownership mismatch: Sale deed purchaser does not match Jamabandi ROR record."),
            ValidationResult(land_record_id=rec2.id, rule_name="AREA_CONSISTENCY", field_name="land_area", is_valid=False, severity="Warning", message="Area discrepancy: 4.10 Acres vs 4.25 Acres in master record."),
        ]
        db.add_all(validations)
        db.commit()

        print("Seeding cross-document conflict graph records...")
        conflicts = [
            ConflictRecord(
                khasra_number="245/1",
                village="Rampur",
                doc_1_title="Jamabandi_2024_Khasra_245.pdf",
                doc_2_title="SaleDeed_Khasra_245_Deed.png",
                conflict_type="Ownership Mismatch",
                description="Jamabandi ROR records owner as 'Ramesh Kumar Sharma', but recent Sale Deed lists purchaser as 'Suresh Kumar Verma' without completed Mutation record.",
                severity="Critical",
                status="Active"
            ),
            ConflictRecord(
                khasra_number="245/1",
                village="Rampur",
                doc_1_title="Jamabandi_2024_Khasra_245.pdf",
                doc_2_title="SaleDeed_Khasra_245_Deed.png",
                conflict_type="Area Discrepancy",
                description="Land area mismatch: Jamabandi states 4.25 Acres (17,199.1 sq.m), whereas Sale Deed states 4.10 Acres (16,592.1 sq.m).",
                severity="High",
                status="Active"
            )
        ]
        db.add_all(conflicts)
        db.commit()

        print("Seeding duplicate candidate pairs...")
        duplicates = [
            DuplicateCandidate(
                record_id_1=rec1.id,
                record_id_2=rec4.id,
                owner_1="Ramesh Kumar Sharma",
                owner_2="Ramesh K. Sharma",
                khasra_number="245/1",
                village="Rampur",
                similarity_score=0.91,
                duplicate_reason="High fuzzy name similarity (91%) & identical Khasra Number (245/1) in Village Rampur.",
                status="Pending"
            )
        ]
        db.add_all(duplicates)
        db.commit()

        print("Seeding audit logs...")
        logs = [
            AuditLog(user_name="System AI Pipeline", user_role="AI Core", action="UPLOAD", target_type="DOCUMENT", target_id="1", details={"filename": "jamabandi_rampur_2024.pdf", "quality": 0.92}),
            AuditLog(user_name="System AI Pipeline", user_role="AI Core", action="OCR_EXTRACT", target_type="RECORD", target_id="1", details={"confidence": 0.94, "fields_extracted": 8}),
            AuditLog(user_name="System AI Pipeline", user_role="AI Core", action="CONFLICT_DETECTED", target_type="CONFLICT", target_id="1", details={"khasra": "245/1", "conflict": "Ownership Mismatch"}),
            AuditLog(user_name="Ananya Verma", user_role="Verifier", action="VERIFY", target_type="RECORD", target_id="1", details={"action": "APPROVED", "remarks": "Document fields verified against legacy registry."}),
        ]
        db.add_all(logs)
        db.commit()

        print("Seeding GIS cadastral plot features...")
        # Coordinates centered around Rampur region (28.8124 N, 79.0250 E)
        plots = [
            MapFeature(
                land_record_id=rec1.id,
                khasra_number="245/1",
                village="Rampur",
                tehsil="Rampur Tehsil",
                district="Rampur District",
                owner_name="Ramesh Kumar Sharma",
                land_area_acres=4.25,
                center_lat=28.8125,
                center_lng=79.0250,
                status="Verified",
                geometry_geojson={
                    "type": "Polygon",
                    "coordinates": [[
                        [79.0240, 28.8120],
                        [79.0260, 28.8120],
                        [79.0260, 28.8130],
                        [79.0240, 28.8130],
                        [79.0240, 28.8120]
                    ]]
                }
            ),
            MapFeature(
                land_record_id=rec2.id,
                khasra_number="245/2",
                village="Rampur",
                tehsil="Rampur Tehsil",
                district="Rampur District",
                owner_name="Suresh Kumar Verma (Conflict)",
                land_area_acres=4.10,
                center_lat=28.8135,
                center_lng=79.0250,
                status="Conflict",
                geometry_geojson={
                    "type": "Polygon",
                    "coordinates": [[
                        [79.0240, 28.8130],
                        [79.0260, 28.8130],
                        [79.0260, 28.8140],
                        [79.0240, 28.8140],
                        [79.0240, 28.8130]
                    ]]
                }
            ),
            MapFeature(
                land_record_id=rec3.id,
                khasra_number="118",
                village="Chandpur",
                tehsil="Rampur Tehsil",
                district="Rampur District",
                owner_name="Priya Devi",
                land_area_acres=6.17,
                center_lat=28.8150,
                center_lng=79.0280,
                status="Verified",
                geometry_geojson={
                    "type": "Polygon",
                    "coordinates": [[
                        [79.0270, 28.8145],
                        [79.0290, 28.8145],
                        [79.0290, 28.8155],
                        [79.0270, 28.8155],
                        [79.0270, 28.8145]
                    ]]
                }
            ),
            MapFeature(
                land_record_id=rec4.id,
                khasra_number="312/B",
                village="Rampur",
                tehsil="Rampur Tehsil",
                district="Rampur District",
                owner_name="Ramesh K. Sharma",
                land_area_acres=4.25,
                center_lat=28.8110,
                center_lng=79.0220,
                status="LowConfidence",
                geometry_geojson={
                    "type": "Polygon",
                    "coordinates": [[
                        [79.0210, 28.8105],
                        [79.0230, 28.8105],
                        [79.0230, 28.8115],
                        [79.0210, 28.8115],
                        [79.0210, 28.8105]
                    ]]
                }
            )
        ]
        db.add_all(plots)
        db.commit()

        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
