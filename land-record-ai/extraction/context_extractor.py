"""Context Window and Spatial Proximity Candidate Ranker."""

import math
from typing import Any, Dict, List, Optional, Tuple
from schemas.fields import FieldCandidate
from schemas.ocr import OCRWord


class ContextWindowExtractor:
    """
    Ranks candidate field values based on 2D spatial proximity to anchor keywords,
    contextual bounding box distance, and OCR token confidence.
    """

    def __init__(self, max_distance_px: float = 600.0):
        self.max_distance_px = max_distance_px

    def rank_candidates(
        self,
        anchor_keywords: List[str],
        words: List[OCRWord],
        candidate_pattern: str,
        engine_name: str = "primary",
        page_number: int = 1
    ) -> List[FieldCandidate]:
        """
        Identify tokens matching candidate_pattern and rank them by proximity to any anchor keyword.
        """
        import re

        # 1. Locate anchor word boxes [x_min, y_min, x_max, y_max]
        anchor_boxes: List[List[int]] = []
        for w in words:
            w_text = (w.normalized_text or w.text).lower()
            if any(ak.lower() in w_text for ak in anchor_keywords):
                anchor_boxes.append(w.bbox)

        candidates: List[FieldCandidate] = []
        for w in words:
            w_text = w.normalized_text or w.text
            match = re.search(candidate_pattern, w_text)
            if match:
                val = match.group(0)
                wb = w.bbox
                cx = (wb[0] + wb[2]) / 2.0
                cy = (wb[1] + wb[3]) / 2.0

                # Compute minimum distance to any anchor box
                min_dist = self.max_distance_px
                if anchor_boxes:
                    for ab in anchor_boxes:
                        # Edge distance
                        dx = max(0, ab[0] - wb[2], wb[0] - ab[2])
                        dy = max(0, ab[1] - wb[3], wb[1] - ab[3])
                        dist = math.hypot(dx, dy)
                        if dist < min_dist:
                            min_dist = dist

                proximity_score = max(0.0, 1.0 - (min_dist / self.max_distance_px))
                regex_validity = 1.0
                context_match = 0.9 if anchor_boxes else 0.5
                ocr_conf = w.confidence

                combined_score = round(
                    0.35 * ocr_conf + 0.35 * proximity_score + 0.20 * regex_validity + 0.10 * context_match,
                    4
                )

                candidates.append(FieldCandidate(
                    value=val,
                    normalized_value=val,
                    ocr_confidence=ocr_conf,
                    keyword_proximity=round(proximity_score, 4),
                    regex_validity=regex_validity,
                    context_match=context_match,
                    combined_score=combined_score,
                    source_engine=engine_name,
                    bbox=w.bbox,
                    page_number=page_number
                ))

        # Sort descending by combined_score
        candidates.sort(key=lambda c: c.combined_score, reverse=True)
        return candidates
