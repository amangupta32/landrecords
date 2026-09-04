"""End-to-End integration tests for Land Record AI pipeline."""

import os
import cv2
import numpy as np
import pytest

from pipeline import LandRecordAIPipeline
from schemas.output import DocumentProcessingOutput


class TestPipelineE2E:
    @pytest.fixture
    def pipeline(self):
        return LandRecordAIPipeline()

    def test_full_pipeline_synthetic_doc(self, pipeline):
        # Create a synthetic image
        img = np.full((600, 800, 3), 255, dtype=np.uint8)
        cv2.putText(img, "SALE DEED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        cv2.putText(img, "Khasra No: 245/1", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        output = pipeline.process(img, document_id="doc_test_001")

        assert isinstance(output, DocumentProcessingOutput)
        assert output.document_id == "doc_test_001"
        assert output.pages == 1
        assert output.document_quality.quality in ["good", "acceptable", "poor"]
        assert output.ocr.primary_engine is not None
        assert len(output.fields.khasra_numbers) >= 1
        assert output.confidence.overall > 0.0
        assert len(output.field_confidences) >= 4
        assert len(output.explanations) >= 2
        assert output.processing_time_ms is not None
        assert output.processing_time_ms > 0

    def test_full_pipeline_raw_sample_if_exists(self, pipeline):
        sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "sample_khasra_doc.png")
        if os.path.exists(sample_path):
            output = pipeline.process(sample_path, document_id="sample_khasra")
            assert output.document_id == "sample_khasra"
            assert isinstance(output, DocumentProcessingOutput)
            assert len(output.fields.khasra_numbers) >= 1
            assert output.fields.land_area.value is not None
