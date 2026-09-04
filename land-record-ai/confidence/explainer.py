"""Natural language explanation generator for multi-level confidence scoring."""

from typing import Any, Dict, List, Optional
from schemas.document import DocumentQuality
from schemas.fields import ExtractedFields
from schemas.ocr import OCRSummary
from schemas.output import ComponentConfidenceScores, FieldConfidenceDetail
from validation.pipeline import ValidationReport


class ConfidenceExplainer:
    """
    Synthesizes multi-factor scoring rationales into clear, actionable human-readable explanations.
    """

    def generate_field_reasons(
        self,
        field_name: str,
        components: ComponentConfidenceScores,
        validation_report: Optional[ValidationReport] = None
    ) -> List[str]:
        """Generate bullet explanations detailing why a field received its confidence score."""
        reasons: List[str] = []

        # OCR Rationale
        if components.ocr >= 0.90:
            reasons.append(f"High-clarity OCR token recognition ({components.ocr * 100:.1f}%)")
        elif components.ocr >= 0.70:
            reasons.append(f"Moderate OCR character confidence ({components.ocr * 100:.1f}%)")
        else:
            reasons.append(f"Low OCR character clarity ({components.ocr * 100:.1f}%) due to document degradation")

        # Extraction Rationale
        if components.extraction >= 0.90:
            reasons.append("Exact keyword anchor match with high spatial proximity")
        elif components.extraction >= 0.70:
            reasons.append("Matched standard pattern with reasonable proximity")
        else:
            reasons.append("Field was inferred from fallback heuristics or distant context")

        # Validation Rationale
        if validation_report and field_name in validation_report.field_scores:
            v_score = validation_report.field_scores[field_name]
            if v_score >= 0.90:
                reasons.append("Passed all state revenue format and schema checks")
            elif v_score >= 0.60:
                reasons.append("Minor format anomaly detected during revenue validation")
            else:
                reasons.append("Validation failed format or boundary constraints")

        # Context Rationale
        if components.context >= 0.80:
            reasons.append("Strong multi-field relational agreement across record")

        return reasons

    def generate_document_explanations(
        self,
        quality: DocumentQuality,
        ocr_summary: OCRSummary,
        fields: ExtractedFields,
        validation_report: ValidationReport,
        overall_score: float,
        needs_review: bool
    ) -> List[str]:
        """Generate top-level document assessment summary."""
        explanations: List[str] = []

        # 1. Quality & OCR
        explanations.append(
            f"Image quality is {quality.quality} (Laplacian blur variance: {quality.laplacian_variance:.1f}, "
            f"contrast: {quality.contrast:.1f})."
        )
        explanations.append(
            f"Primary OCR engine '{ocr_summary.primary_engine}' recognized text with "
            f"{ocr_summary.average_confidence * 100:.1f}% average token confidence."
        )

        # 2. Extracted Entities
        khasra_str = ", ".join(k.value for k in fields.khasra_numbers) if fields.khasra_numbers else "None"
        owner_str = ", ".join(o.name for o in fields.owner_names) if fields.owner_names else "None"
        explanations.append(f"Identified Khasra parcel: {khasra_str}; Tenure holder: {owner_str}.")

        # 3. Location & Area
        if fields.location.village and fields.location.state:
            explanations.append(
                f"Administrative hierarchy verified: Village {fields.location.village}, "
                f"Tehsil {fields.location.tehsil}, District {fields.location.district}, State {fields.location.state}."
            )

        if fields.land_area.value is not None:
            explanations.append(f"Land area extracted: {fields.land_area.value} {fields.land_area.unit or ''}.")

        # 4. Review recommendation
        if needs_review:
            explanations.append("Human review is recommended to confirm flagged field values before final registry.")
        else:
            explanations.append("All fields passed automated validation with high confidence; eligible for straight-through processing.")

        return explanations
