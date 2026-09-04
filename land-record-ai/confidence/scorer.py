"""Explainable Confidence Scoring Engine implementing 4-factor scoring breakdown."""

import os
from typing import Any, Dict, List, Optional, Tuple
import yaml

from confidence.explainer import ConfidenceExplainer
from confidence.tiers import ConfidenceTierClassifier
from schemas.document import DocumentQuality
from schemas.fields import ExtractedFields
from schemas.ocr import OCRSummary
from schemas.output import ComponentConfidenceScores, DocumentConfidence, FieldConfidenceDetail
from validation.pipeline import ValidationReport


class ExplainableConfidenceScorer:
    """
    Computes explainable confidence scores using 4-tiered scoring:
    Confidence = OCR_Weight * OCR + Extraction_Weight * Extraction + Validation_Weight * Validation + Context_Weight * Context
    """

    DEFAULT_WEIGHTS = {
        "ocr": 0.40,
        "extraction": 0.30,
        "validation": 0.20,
        "context": 0.10
    }

    def __init__(self, thresholds_config_path: Optional[str] = None):
        self.weights = self.DEFAULT_WEIGHTS.copy()
        self._load_config(thresholds_config_path)
        self.classifier = ConfidenceTierClassifier()
        self.explainer = ConfidenceExplainer()

    def _load_config(self, config_path: Optional[str]) -> None:
        path = config_path or os.path.join(os.path.dirname(__file__), "..", "config", "thresholds.yaml")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    w_cfg = data.get("confidence", {}).get("weights", {})
                    if w_cfg:
                        self.weights["ocr"] = float(w_cfg.get("ocr", self.weights["ocr"]))
                        self.weights["extraction"] = float(w_cfg.get("extraction", self.weights["extraction"]))
                        self.weights["validation"] = float(w_cfg.get("validation", self.weights["validation"]))
                        self.weights["context"] = float(w_cfg.get("context", self.weights["context"]))
            except Exception:
                pass

    def compute_field_score(
        self,
        field_name: str,
        ocr_conf: float,
        extraction_conf: float,
        validation_conf: float,
        context_conf: float,
        validation_report: Optional[ValidationReport] = None
    ) -> FieldConfidenceDetail:
        """Calculate weighted score and explainability detail for an individual field."""
        components = ComponentConfidenceScores(
            ocr=round(max(0.0, min(1.0, ocr_conf)), 4),
            extraction=round(max(0.0, min(1.0, extraction_conf)), 4),
            validation=round(max(0.0, min(1.0, validation_conf)), 4),
            context=round(max(0.0, min(1.0, context_conf)), 4)
        )

        weighted_score = (
            self.weights["ocr"] * components.ocr +
            self.weights["extraction"] * components.extraction +
            self.weights["validation"] * components.validation +
            self.weights["context"] * components.context
        )
        final_score = round(max(0.0, min(1.0, weighted_score)), 4)
        tier = self.classifier.classify(final_score)
        reasons = self.explainer.generate_field_reasons(field_name, components, validation_report)

        return FieldConfidenceDetail(
            score=final_score,
            tier=tier,
            components=components,
            reasons=reasons
        )

    def score_document(
        self,
        quality: DocumentQuality,
        ocr_summary: OCRSummary,
        fields: ExtractedFields,
        validation_report: ValidationReport
    ) -> Tuple[DocumentConfidence, Dict[str, FieldConfidenceDetail], List[str], bool]:
        """
        Compute full document-level explainable confidence breakdown.
        """
        field_confidences: Dict[str, FieldConfidenceDetail] = {}
        base_ocr_conf = ocr_summary.average_confidence

        # 1. Khasra Numbers
        khasra_ext_conf = fields.khasra_numbers[0].confidence if fields.khasra_numbers else 0.0
        khasra_val_conf = validation_report.field_scores.get("khasra_numbers", 1.0)
        field_confidences["khasra_numbers"] = self.compute_field_score(
            "khasra_numbers",
            ocr_conf=base_ocr_conf,
            extraction_conf=khasra_ext_conf,
            validation_conf=khasra_val_conf,
            context_conf=0.95 if fields.khasra_numbers else 0.20,
            validation_report=validation_report
        )

        # 2. Khata Numbers
        khata_ext_conf = fields.khata_numbers[0].confidence if fields.khata_numbers else 0.70
        khata_val_conf = validation_report.field_scores.get("khata_numbers", 1.0)
        field_confidences["khata_numbers"] = self.compute_field_score(
            "khata_numbers",
            ocr_conf=base_ocr_conf,
            extraction_conf=khata_ext_conf,
            validation_conf=khata_val_conf,
            context_conf=0.90 if fields.khata_numbers else 0.50,
            validation_report=validation_report
        )

        # 3. Land Area
        area_ext_conf = fields.land_area.confidence
        area_val_conf = validation_report.field_scores.get("land_area", 1.0)
        field_confidences["land_area"] = self.compute_field_score(
            "land_area",
            ocr_conf=base_ocr_conf,
            extraction_conf=area_ext_conf,
            validation_conf=area_val_conf,
            context_conf=0.92 if fields.land_area.value is not None else 0.20,
            validation_report=validation_report
        )

        # 4. Owner Names
        owner_ext_conf = fields.owner_names[0].confidence if fields.owner_names else 0.0
        owner_val_conf = validation_report.field_scores.get("owner_names", 1.0)
        field_confidences["owner_names"] = self.compute_field_score(
            "owner_names",
            ocr_conf=base_ocr_conf,
            extraction_conf=owner_ext_conf,
            validation_conf=owner_val_conf,
            context_conf=0.95 if fields.owner_names else 0.20,
            validation_report=validation_report
        )

        # 5. Location Hierarchy
        loc_ext_conf = fields.location.confidence
        loc_val_conf = validation_report.field_scores.get("location", 1.0)
        field_confidences["location"] = self.compute_field_score(
            "location",
            ocr_conf=base_ocr_conf,
            extraction_conf=loc_ext_conf,
            validation_conf=loc_val_conf,
            context_conf=0.95 if fields.location.is_valid_hierarchy else 0.50,
            validation_report=validation_report
        )

        # 6. Overall Document Confidence
        field_score_vals = [fc.score for fc in field_confidences.values()]
        overall_score = round(sum(field_score_vals) / len(field_score_vals), 4) if field_score_vals else 0.85
        doc_tier = self.classifier.classify(overall_score)
        doc_confidence = DocumentConfidence(overall=overall_score, tier=doc_tier)

        # 7. Human Review Requirement
        raw_field_scores = {fn: fc.score for fn, fc in field_confidences.items()}
        needs_review = self.classifier.check_human_review_required(
            overall_score=overall_score,
            field_scores=raw_field_scores,
            blur_grade=quality.quality
        )

        # 8. Explanations
        explanations = self.explainer.generate_document_explanations(
            quality=quality,
            ocr_summary=ocr_summary,
            fields=fields,
            validation_report=validation_report,
            overall_score=overall_score,
            needs_review=needs_review
        )

        return doc_confidence, field_confidences, explanations, needs_review
