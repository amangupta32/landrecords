"""Confidence tier classification and human review routing."""

from typing import Any, Dict, List, Optional
from schemas.output import ConfidenceTier


class ConfidenceTierClassifier:
    """Classifies numerical confidence scores (0.0 to 1.0) into operational tiers."""

    @staticmethod
    def classify(score: float) -> ConfidenceTier:
        """Assign ConfidenceTier enum based on thresholds."""
        if score >= 0.90:
            return ConfidenceTier.VERY_HIGH
        elif score >= 0.75:
            return ConfidenceTier.HIGH
        elif score >= 0.50:
            return ConfidenceTier.MEDIUM
        else:
            return ConfidenceTier.LOW

    @staticmethod
    def check_human_review_required(
        overall_score: float,
        field_scores: Dict[str, float],
        blur_grade: Optional[str] = None
    ) -> bool:
        """
        Determines whether human-in-the-loop review is mandatory:
        - Overall confidence < 0.75 (MEDIUM or LOW)
        - Crucial field (khasra_numbers, owner_names, land_area) score < 0.75
        - Document quality is BLURRY or POOR
        """
        if overall_score < 0.75:
            return True

        critical_fields = ["khasra_numbers", "owner_names", "land_area"]
        for cf in critical_fields:
            if cf in field_scores and field_scores[cf] < 0.75:
                return True

        if blur_grade and blur_grade.upper() in ["BLURRY", "POOR", "LOW"]:
            return True

        return False
