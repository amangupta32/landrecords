from typing import Dict, Any
from app.core.config import settings

class ExplainableConfidenceEngine:
    def __init__(self):
        self.w_ocr = settings.WEIGHT_OCR          # 0.40
        self.w_ext = settings.WEIGHT_EXTRACTION    # 0.30
        self.w_val = settings.WEIGHT_VALIDATION    # 0.20
        self.w_ctx = settings.WEIGHT_CONTEXT       # 0.10

    def compute_field_confidence(
        self,
        field_name: str,
        ocr_conf: float,
        extraction_conf: float,
        validation_conf: float,
        context_conf: float = 0.90,
        is_edited: bool = False,
        validation_messages: list = None
    ) -> Dict[str, Any]:
        """
        Calculates weighted composite score and constructs human-readable explainability rationale.
        """
        if is_edited:
            return {
                "ocr_confidence": 1.00,
                "extraction_confidence": 1.00,
                "validation_confidence": 1.00,
                "context_confidence": 1.00,
                "final_confidence": 1.00,
                "confidence_explanation": "Verified & manually edited by Human Verifier (100% Verified)."
            }

        raw_score = (
            self.w_ocr * ocr_conf +
            self.w_ext * extraction_conf +
            self.w_val * validation_conf +
            self.w_ctx * context_conf
        )
        final_score = round(min(1.0, max(0.0, raw_score)), 2)

        # Generate Human-Readable Explainability Rationale
        explanations = []

        if ocr_conf < 0.70:
            explanations.append(f"Low OCR confidence ({int(ocr_conf * 100)}%) due to character degradation or handwriting ambiguity.")
        elif ocr_conf > 0.90:
            explanations.append("High OCR character recognition precision.")

        if extraction_conf < 0.70:
            explanations.append("Non-standard field layout structure or missing delimiter keywords.")

        if validation_conf < 1.0 and validation_messages:
            for msg in validation_messages:
                explanations.append(f"Validation alert: {msg}")
        elif validation_conf == 1.0:
            explanations.append("Successfully passed all database schema and location format validations.")

        if final_score >= 0.85:
            explanation_text = "High Confidence: " + " ".join(explanations)
        elif final_score >= 0.65:
            explanation_text = "Medium Confidence: " + " ".join(explanations)
        else:
            explanation_text = "Attention Required (Low Confidence): " + " ".join(explanations)

        return {
            "ocr_confidence": round(ocr_conf, 2),
            "extraction_confidence": round(extraction_conf, 2),
            "validation_confidence": round(validation_conf, 2),
            "context_confidence": round(context_conf, 2),
            "final_confidence": final_score,
            "confidence_explanation": explanation_text
        }

confidence_engine = ExplainableConfidenceEngine()
