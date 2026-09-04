"""OCR Ensemble: Combines predictions across multiple OCR engines and measures agreement."""

from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple
from ocr.normalizer import OCRNormalizer
from schemas.ocr import OCREngineResult, OCRLine, OCRSummary, OCRWord


class OCREnsemble:
    """
    Ensemble module that combines outputs from multiple OCR engines,
    measures character & token agreement, and yields higher-confidence text predictions.
    """

    def __init__(self, normalizer: Optional[OCRNormalizer] = None):
        self.normalizer = normalizer or OCRNormalizer()

    def compute_agreement(self, text_a: str, text_b: str) -> float:
        """Calculate similarity ratio between two OCR text strings (0.0 to 1.0)."""
        if not text_a and not text_b:
            return 1.0
        if not text_a or not text_b:
            return 0.0
        matcher = SequenceMatcher(None, text_a.strip(), text_b.strip())
        return round(float(matcher.ratio()), 4)

    def ensemble_results(self, results: List[OCREngineResult]) -> Tuple[OCREngineResult, OCRSummary]:
        """
        Merge multiple OCREngineResult objects into an ensemble consensus result.
        """
        if not results:
            raise ValueError("No OCR results provided to ensemble.")

        if len(results) == 1:
            primary = results[0]
            summary = OCRSummary(
                primary_engine=primary.engine,
                fallback_used=(primary.engine == "fallback"),
                average_confidence=primary.average_confidence,
                engines_executed=[primary.engine],
                agreement_score=1.0
            )
            return primary, summary

        # Sort by average confidence descending
        sorted_results = sorted(results, key=lambda r: r.average_confidence, reverse=True)
        primary = sorted_results[0]

        # Calculate pairwise agreement with primary
        agreements = [
            self.compute_agreement(primary.normalized_text or primary.text, r.normalized_text or r.text)
            for r in sorted_results[1:]
        ]
        avg_agreement = sum(agreements) / len(agreements) if agreements else 1.0

        # Create ensemble output based on primary with boosted confidence when engines agree
        boosted_words: List[OCRWord] = []
        for word in primary.words:
            # Boost confidence slightly if agreement is high
            adjusted_conf = min(1.0, word.confidence * (0.8 + 0.2 * avg_agreement))
            boosted_words.append(OCRWord(
                text=word.text,
                normalized_text=word.normalized_text,
                bbox=word.bbox,
                confidence=round(adjusted_conf, 4)
            ))

        boosted_lines: List[OCRLine] = []
        for line in primary.lines:
            adjusted_line_conf = min(1.0, line.confidence * (0.8 + 0.2 * avg_agreement))
            boosted_lines.append(OCRLine(
                text=line.text,
                normalized_text=line.normalized_text,
                words=line.words,
                bbox=line.bbox,
                confidence=round(adjusted_line_conf, 4)
            ))

        ensemble_conf = min(1.0, primary.average_confidence * (0.85 + 0.15 * avg_agreement))

        ensemble_result = OCREngineResult(
            engine="ensemble",
            language=primary.language,
            text=primary.text,
            normalized_text=primary.normalized_text,
            words=boosted_words,
            lines=boosted_lines,
            page_number=primary.page_number,
            average_confidence=round(ensemble_conf, 4),
            metadata={
                "base_engines": [r.engine for r in results],
                "agreement_score": round(avg_agreement, 4)
            }
        )

        summary = OCRSummary(
            primary_engine="ensemble",
            fallback_used=any(r.engine == "fallback" for r in results),
            average_confidence=round(ensemble_conf, 4),
            engines_executed=[r.engine for r in results],
            agreement_score=round(avg_agreement, 4)
        )

        return ensemble_result, summary
