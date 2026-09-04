"""Unit tests for Pydantic schemas and serialization."""

import pytest
from schemas.document import DocumentQuality, DeskewMetadata, PreprocessingMetadata
from schemas.ocr import OCRWord, OCRLine, OCREngineResult, OCRSummary, BoundingBox
from schemas.fields import (
    OwnerField,
    KhasraField,
    KhataField,
    AreaField,
    LocationHierarchyField,
    MutationField,
    DateField,
    ExtractedFields,
    FieldCandidate,
)
from schemas.output import (
    ConfidenceTier,
    ComponentConfidenceScores,
    FieldConfidenceDetail,
    DocumentConfidence,
    DocumentProcessingOutput,
)


class TestSchemas:
    """Test instantiation, serialization, and constraints of data models."""

    def test_bounding_box_methods(self):
        bbox = BoundingBox(x_min=10, y_min=20, x_max=110, y_max=70)
        assert bbox.as_list == [10, 20, 110, 70]
        assert bbox.center == (60.0, 45.0)
        assert bbox.width == 100
        assert bbox.height == 50

    def test_document_quality_schema(self):
        dq = DocumentQuality(
            laplacian_variance=342.5,
            quality="good",
            brightness=140.2,
            contrast=45.6,
            width=1200,
            height=1600,
            dpi=300,
            is_blurry=False
        )
        data = dq.model_dump()
        assert data["laplacian_variance"] == 342.5
        assert data["quality"] == "good"

    def test_ocr_models(self):
        word = OCRWord(text="खसरा", bbox=[100, 200, 180, 230], confidence=0.96)
        res = OCREngineResult(
            engine="paddleocr",
            language="hin",
            text="खसरा 123",
            words=[word],
            average_confidence=0.96
        )
        assert res.engine == "paddleocr"
        assert len(res.words) == 1
        assert res.words[0].text == "खसरा"

    def test_fields_models(self):
        owner = OwnerField(name="Ram Singh", relation_type="S/O", relation_name="Mohan Singh", confidence=0.92, tier="VERY_HIGH")
        khasra = KhasraField(value="123/1", confidence=0.95, tier="VERY_HIGH")
        khata = KhataField(value="456", confidence=0.94, tier="VERY_HIGH")
        area = AreaField(value=2.5, unit="hectare", raw_text="2.5000 हेक्टेयर", confidence=0.88, tier="HIGH")
        loc = LocationHierarchyField(village="Rajpur", tehsil="Dehradun", district="Dehradun", state="Uttarakhand", confidence=0.91, tier="VERY_HIGH")
        mut = MutationField(mutation_number="MUT-2024-001", confidence=0.85, tier="HIGH")
        dt = DateField(iso_date="2024-01-15", raw_date="15/01/2024", confidence=0.95, tier="VERY_HIGH")

        fields = ExtractedFields(
            owner_names=[owner],
            khasra_numbers=[khasra],
            khata_numbers=[khata],
            land_area=area,
            location=loc,
            mutation_reference=mut,
            record_date=dt
        )
        assert len(fields.owner_names) == 1
        assert fields.khasra_numbers[0].value == "123/1"
        assert fields.land_area.value == 2.5
        assert fields.location.district == "Dehradun"

    def test_canonical_document_output_schema(self):
        output = DocumentProcessingOutput(
            document_id="doc_001",
            pages=1,
            document_quality=DocumentQuality(
                laplacian_variance=342.5,
                quality="good",
                brightness=150.0,
                contrast=50.0,
                width=1000,
                height=1400
            ),
            ocr=OCRSummary(
                primary_engine="paddleocr",
                fallback_used=False,
                average_confidence=0.93,
                engines_executed=["paddleocr"]
            ),
            fields=ExtractedFields(),
            confidence=DocumentConfidence(
                overall=0.91,
                tier=ConfidenceTier.VERY_HIGH
            ),
            explanations=[
                "OCR confidence was high.",
                "Candidate appeared near the Khasra field label."
            ],
            needs_human_review=False
        )
        json_dict = output.model_dump()
        assert json_dict["document_id"] == "doc_001"
        assert json_dict["confidence"]["tier"] == "VERY_HIGH"
        assert len(json_dict["explanations"]) == 2
