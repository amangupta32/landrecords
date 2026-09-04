"""Unit tests for Explainable Confidence Engine, tiering, and explanations."""

import pytest
from confidence.explainer import ConfidenceExplainer
from confidence.scorer import ExplainableConfidenceScorer
from confidence.tiers import ConfidenceTierClassifier
from schemas.document import DocumentQuality
from schemas.fields import AreaField, ExtractedFields, KhasraField, KhataField, LocationHierarchyField, OwnerField
from schemas.ocr import OCRSummary
from schemas.output import ConfidenceTier
from validation.pipeline import ValidationReport


class TestConfidenceTierClassifier:
    def test_tier_thresholds(self):
        assert ConfidenceTierClassifier.classify(0.95) == ConfidenceTier.VERY_HIGH
        assert ConfidenceTierClassifier.classify(0.90) == ConfidenceTier.VERY_HIGH
        assert ConfidenceTierClassifier.classify(0.85) == ConfidenceTier.HIGH
        assert ConfidenceTierClassifier.classify(0.75) == ConfidenceTier.HIGH
        assert ConfidenceTierClassifier.classify(0.60) == ConfidenceTier.MEDIUM
        assert ConfidenceTierClassifier.classify(0.40) == ConfidenceTier.LOW

    def test_human_review_triggers(self):
        # Overall < 0.75 -> True
        assert ConfidenceTierClassifier.check_human_review_required(0.70, {"khasra_numbers": 0.9}) is True
        
        # Critical field < 0.75 -> True
        assert ConfidenceTierClassifier.check_human_review_required(0.85, {"khasra_numbers": 0.60}) is True

        # All high -> False
        assert ConfidenceTierClassifier.check_human_review_required(
            0.92,
            {"khasra_numbers": 0.95, "owner_names": 0.90, "land_area": 0.92},
            blur_grade="EXCELLENT"
        ) is False

        # Blurry document -> True
        assert ConfidenceTierClassifier.check_human_review_required(
            0.92,
            {"khasra_numbers": 0.95, "owner_names": 0.90, "land_area": 0.92},
            blur_grade="BLURRY"
        ) is True


class TestExplainableConfidenceScorer:
    @pytest.fixture
    def scorer(self):
        return ExplainableConfidenceScorer()

    def test_compute_field_score_formula(self, scorer):
        # OCR=1.0, Extraction=1.0, Validation=1.0, Context=1.0 -> 1.0
        detail = scorer.compute_field_score("khasra_numbers", 1.0, 1.0, 1.0, 1.0)
        assert detail.score == 1.0
        assert detail.tier == ConfidenceTier.VERY_HIGH
        assert len(detail.reasons) > 0

    def test_score_document_full(self, scorer):
        quality = DocumentQuality(
            laplacian_variance=250.0,
            contrast=75.0,
            quality="good",
            width=800,
            height=600,
            brightness=128.0,
            is_blurry=False
        )
        ocr_summary = OCRSummary(primary_engine="fallback", average_confidence=0.95)
        fields = ExtractedFields(
            owner_names=[OwnerField(name="Ramesh Kumar Sharma", confidence=0.96)],
            khasra_numbers=[KhasraField(value="245/1", confidence=0.95)],
            khata_numbers=[KhataField(value="89", confidence=0.92)],
            land_area=AreaField(value=4.25, unit="acre", confidence=0.90),
            location=LocationHierarchyField(
                village="Rampur",
                tehsil="Rampur Tehsil",
                district="Rampur District",
                state="Uttar Pradesh",
                confidence=0.95,
                is_valid_hierarchy=True
            )
        )
        val_report = ValidationReport(
            validation_score=0.98,
            is_valid=True,
            field_scores={"khasra_numbers": 1.0, "owner_names": 1.0, "land_area": 1.0, "location": 1.0}
        )

        doc_conf, field_confs, explanations, needs_review = scorer.score_document(
            quality=quality,
            ocr_summary=ocr_summary,
            fields=fields,
            validation_report=val_report
        )

        assert doc_conf.overall >= 0.85
        assert doc_conf.tier in [ConfidenceTier.VERY_HIGH, ConfidenceTier.HIGH]
        assert "khasra_numbers" in field_confs
        assert "owner_names" in field_confs
        assert len(explanations) >= 3
        assert needs_review is False
