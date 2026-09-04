"""Text and bounding box normalization for OCR outputs."""

import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import yaml

from schemas.ocr import BoundingBox, OCREngineResult, OCRLine, OCRWord


class OCRNormalizer:
    """Normalizes OCR recognized text (Indic numerals, punctuation, whitespace) and spatial coordinates."""

    DEFAULT_DEVANAGARI_DIGITS = {
        "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
        "५": "5", "६": "6", "७": "7", "८": "8", "९": "9"
    }

    DEFAULT_PUNCTUATION = {
        "।": ".",
        "॥": ".",
        "—": "-",
        "–": "-"
    }

    def __init__(self, languages_config_path: Optional[str] = None):
        self.numeral_map = self.DEFAULT_DEVANAGARI_DIGITS.copy()
        self.punctuation_map = self.DEFAULT_PUNCTUATION.copy()

        if languages_config_path and os.path.exists(languages_config_path):
            self._load_config(languages_config_path)
        else:
            default_path = os.path.join(os.path.dirname(__file__), "..", "config", "languages.yaml")
            if os.path.exists(default_path):
                self._load_config(default_path)

        # Build translation table
        combined = {**self.numeral_map, **self.punctuation_map}
        self.translation_table = str.maketrans(combined)

    def _load_config(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                devanagari_map = data.get("indic_numerals", {}).get("devanagari", {})
                if devanagari_map:
                    self.numeral_map.update({str(k): str(v) for k, v in devanagari_map.items()})
                punct_map = data.get("punctuation_mappings", {})
                if punct_map:
                    self.punctuation_map.update({str(k): str(v) for k, v in punct_map.items()})
        except Exception:
            pass

    def normalize_text(self, text: str) -> str:
        """
        Normalize raw OCR text:
        1. Translates Devanagari numerals (०-९) to ASCII (0-9).
        2. Normalizes punctuation (। -> .).
        3. Collapses multiple spaces and strips extraneous whitespace.
        """
        if not text:
            return ""
        normalized = text.translate(self.translation_table)
        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()

    def normalize_bbox(
        self,
        bbox: Union[List[int], Tuple[int, ...], BoundingBox],
        img_width: Optional[int] = None,
        img_height: Optional[int] = None,
        is_xywh: bool = False
    ) -> List[int]:
        """
        Standardize bounding box to [x_min, y_min, x_max, y_max].
        Supports [x, y, w, h] or 4-corner polygon formats.
        """
        if isinstance(bbox, BoundingBox):
            x_min, y_min, x_max, y_max = bbox.x_min, bbox.y_min, bbox.x_max, bbox.y_max
        elif is_xywh and len(bbox) == 4:
            x, y, w, h = bbox
            x_min, y_min, x_max, y_max = int(x), int(y), int(x + w), int(y + h)
        elif len(bbox) == 4 and not is_xywh:
            x_min, y_min, x_max, y_max = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        elif len(bbox) == 8:  # Polygon format [x1, y1, x2, y2, x3, y3, x4, y4]
            xs = [bbox[i] for i in range(0, 8, 2)]
            ys = [bbox[i] for i in range(1, 8, 2)]
            x_min, y_min, x_max, y_max = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
        else:
            x_min, y_min, x_max, y_max = 0, 0, 0, 0

        # Enforce canonical ordering
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        if y_min > y_max:
            y_min, y_max = y_max, y_min

        # Enforce non-negativity
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = max(0, x_max)
        y_max = max(0, y_max)

        # Clamp to image boundaries if provided
        if img_width is not None and img_width > 0:
            x_min = min(x_min, img_width)
            x_max = min(x_max, img_width)
        if img_height is not None and img_height > 0:
            y_min = min(y_min, img_height)
            y_max = min(y_max, img_height)

        return [x_min, y_min, x_max, y_max]

    def normalize_polygon_points(self, points: List[List[Union[int, float]]]) -> List[int]:
        """Convert list of 4 points [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] to [x_min, y_min, x_max, y_max]."""
        if not points:
            return [0, 0, 0, 0]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]

    def normalize_result(
        self,
        result: OCREngineResult,
        img_width: Optional[int] = None,
        img_height: Optional[int] = None
    ) -> OCREngineResult:
        """
        Apply full normalization over an OCREngineResult object in-place.
        """
        # 1. Normalize full text
        result.normalized_text = self.normalize_text(result.text)

        # 2. Normalize words
        for word in result.words:
            word.normalized_text = self.normalize_text(word.text)
            word.bbox = self.normalize_bbox(word.bbox, img_width=img_width, img_height=img_height)
            # Clamp confidence to [0.0, 1.0]
            word.confidence = max(0.0, min(1.0, float(word.confidence)))

        # 3. Normalize lines
        for line in result.lines:
            line.normalized_text = self.normalize_text(line.text)
            if line.bbox:
                line.bbox = self.normalize_bbox(line.bbox, img_width=img_width, img_height=img_height)
            elif line.words:
                # Infer line bbox from words
                xs = [w.bbox[0] for w in line.words] + [w.bbox[2] for w in line.words]
                ys = [w.bbox[1] for w in line.words] + [w.bbox[3] for w in line.words]
                line.bbox = [min(xs), min(ys), max(xs), max(ys)]
            line.confidence = max(0.0, min(1.0, float(line.confidence)))

        # 4. Compute overall average confidence if not set
        if result.words:
            conf_scores = [w.confidence for w in result.words if w.confidence > 0]
            if conf_scores:
                result.average_confidence = round(float(sum(conf_scores) / len(conf_scores)), 4)

        return result
