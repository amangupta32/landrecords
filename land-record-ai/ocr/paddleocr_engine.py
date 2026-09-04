"""PaddleOCR Engine wrapper for robust multilingual document detection & recognition."""

import os
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image

from ocr.base import OCREngine
from ocr.normalizer import OCRNormalizer
from schemas.ocr import OCREngineResult, OCRLine, OCRWord


class PaddleOCREngine(OCREngine):
    """PaddleOCR engine implementation with multilingual text detection and recognition."""

    def __init__(self, default_language: str = "hi", normalizer: Optional[OCRNormalizer] = None):
        super().__init__(name="paddleocr", default_language=default_language)
        self.normalizer = normalizer or OCRNormalizer()
        self._ocr_instance = None
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check if paddleocr package and paddlepaddle are importable."""
        if self._available is not None:
            return self._available
        try:
            import paddleocr  # noqa: F401
            self._available = True
        except ImportError:
            self._available = False
        except Exception:
            self._available = False
        return self._available

    def _get_engine(self, lang: str):
        if self._ocr_instance is None:
            from paddleocr import PaddleOCR
            self._ocr_instance = PaddleOCR(
                use_angle_cls=True,
                lang=lang,
                show_log=False,
                use_gpu=False
            )
        return self._ocr_instance

    def recognize(
        self,
        image: Union[np.ndarray, Image.Image, str],
        language: Optional[str] = None,
        **kwargs: Any
    ) -> OCREngineResult:
        """
        Run PaddleOCR recognition.
        """
        if not self.is_available():
            raise RuntimeError(
                "PaddleOCR is not available in the current environment. "
                "Install via `pip install paddlepaddle paddleocr` or use LandRecordFallbackEngine."
            )

        lang = language or self.default_language
        ocr = self._get_engine(lang)

        # Prepare numpy array (BGR or RGB)
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image not found: {image}")
            import cv2
            img_np = cv2.imread(image)
        elif isinstance(image, Image.Image):
            img_np = np.array(image.convert("RGB"))
        elif isinstance(image, np.ndarray):
            img_np = image
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")

        h, w = img_np.shape[:2]
        raw_result = ocr.ocr(img_np, cls=True)

        lines: List[OCRLine] = []
        all_words: List[OCRWord] = []
        all_text_lines: List[str] = []

        if raw_result and len(raw_result) > 0 and raw_result[0] is not None:
            for item in raw_result[0]:
                poly_box = item[0]  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                text, conf = item[1]

                bbox = self.normalizer.normalize_polygon_points(poly_box)
                confidence = max(0.0, min(1.0, float(conf)))

                # Split line into words
                raw_words = text.split()
                line_words: List[OCRWord] = []
                
                # Approximate word bboxes proportionally along width
                line_w = max(1, bbox[2] - bbox[0])
                num_words = len(raw_words)
                for idx, rw in enumerate(raw_words):
                    if num_words == 1:
                        w_bbox = bbox
                    else:
                        sub_w = line_w / num_words
                        w_x1 = int(bbox[0] + idx * sub_w)
                        w_x2 = int(bbox[0] + (idx + 1) * sub_w)
                        w_bbox = [w_x1, bbox[1], w_x2, bbox[3]]

                    word_obj = OCRWord(
                        text=rw,
                        normalized_text=self.normalizer.normalize_text(rw),
                        bbox=w_bbox,
                        confidence=confidence
                    )
                    line_words.append(word_obj)
                    all_words.append(word_obj)

                all_text_lines.append(text)
                lines.append(OCRLine(
                    text=text,
                    normalized_text=self.normalizer.normalize_text(text),
                    words=line_words,
                    bbox=bbox,
                    confidence=round(confidence, 4)
                ))

        full_text = "\n".join(all_text_lines)
        conf_scores = [w.confidence for w in all_words if w.confidence > 0]
        avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else 0.85

        result = OCREngineResult(
            engine=self.name,
            language=lang,
            text=full_text,
            normalized_text=self.normalizer.normalize_text(full_text),
            words=all_words,
            lines=lines,
            page_number=1,
            average_confidence=round(avg_conf, 4),
            metadata={"num_detected_lines": len(lines)}
        )

        return self.normalizer.normalize_result(result, img_width=w, img_height=h)
