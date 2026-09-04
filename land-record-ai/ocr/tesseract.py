"""Tesseract OCR Engine wrapper with Hindi, English, and bilingual support."""

import os
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image

from ocr.base import OCREngine
from ocr.normalizer import OCRNormalizer
from schemas.ocr import OCREngineResult, OCRLine, OCRWord

try:
    import pytesseract
    PYTESSERACT_INSTALLED = True
except ImportError:
    PYTESSERACT_INSTALLED = False


class TesseractEngine(OCREngine):
    """OCR engine utilizing Google Tesseract for printed and high-quality documents."""

    def __init__(self, default_language: str = "hin+eng", normalizer: Optional[OCRNormalizer] = None):
        super().__init__(name="tesseract", default_language=default_language)
        self.normalizer = normalizer or OCRNormalizer()
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check if pytesseract library is importable and tesseract executable is in PATH."""
        if self._available is not None:
            return self._available
        if not PYTESSERACT_INSTALLED:
            self._available = False
            return False
        try:
            _ = pytesseract.get_tesseract_version()
            self._available = True
        except Exception:
            self._available = False
        return self._available

    def _prepare_image(self, image: Union[np.ndarray, Image.Image, str]) -> Tuple[Image.Image, int, int]:
        """Convert input to PIL Image and extract width, height."""
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image path not found: {image}")
            pil_img = Image.open(image)
        elif isinstance(image, np.ndarray):
            if len(image.shape) == 2:
                pil_img = Image.fromarray(image)
            elif len(image.shape) == 3:
                # Assuming BGR for OpenCV numpy arrays
                pil_img = Image.fromarray(image[:, :, ::-1])
            else:
                raise ValueError(f"Unsupported numpy image shape: {image.shape}")
        elif isinstance(image, Image.Image):
            pil_img = image
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")

        w, h = pil_img.size
        return pil_img, w, h

    def recognize(
        self,
        image: Union[np.ndarray, Image.Image, str],
        language: Optional[str] = None,
        psm: int = 3,
        oem: int = 3,
        **kwargs: Any
    ) -> OCREngineResult:
        """
        Run Tesseract OCR on the given document image.
        """
        if not self.is_available():
            raise RuntimeError(
                "Tesseract OCR is not available on this host. "
                "Please install Tesseract binary and language packs (tesseract-ocr-hin, tesseract-ocr-eng) "
                "or use LandRecordFallbackEngine."
            )

        lang = language or self.default_language
        pil_img, img_w, img_h = self._prepare_image(image)

        custom_config = f"--oem {oem} --psm {psm}"
        
        # 1. Extract full text
        full_text = pytesseract.image_to_string(pil_img, lang=lang, config=custom_config)

        # 2. Extract detailed word tokens and bounding boxes
        data = pytesseract.image_to_data(pil_img, lang=lang, config=custom_config, output_type=pytesseract.Output.DICT)

        words: List[OCRWord] = []
        lines_dict: Dict[Tuple[int, int, int], List[OCRWord]] = {}  # (page, block, line_num) -> words

        num_entries = len(data.get("text", []))
        for i in range(num_entries):
            raw_text = data["text"][i]
            conf_val = float(data["conf"][i])

            if raw_text and raw_text.strip() and conf_val >= 0:
                clean_word = raw_text.strip()
                left = int(data["left"][i])
                top = int(data["top"][i])
                w = int(data["width"][i])
                h = int(data["height"][i])
                
                # Convert xywh to [x_min, y_min, x_max, y_max]
                bbox = self.normalizer.normalize_bbox([left, top, w, h], img_width=img_w, img_height=img_h, is_xywh=True)
                confidence = max(0.0, min(1.0, conf_val / 100.0))

                word_obj = OCRWord(
                    text=clean_word,
                    normalized_text=self.normalizer.normalize_text(clean_word),
                    bbox=bbox,
                    confidence=confidence
                )
                words.append(word_obj)

                page_num = data.get("page_num", [1])[i]
                block_num = data.get("block_num", [1])[i]
                line_num = data.get("line_num", [1])[i]
                key = (page_num, block_num, line_num)
                lines_dict.setdefault(key, []).append(word_obj)

        # 3. Assemble Lines
        lines: List[OCRLine] = []
        for key, line_words in lines_dict.items():
            line_text = " ".join(w.text for w in line_words)
            line_conf = sum(w.confidence for w in line_words) / len(line_words) if line_words else 1.0
            xs = [w.bbox[0] for w in line_words] + [w.bbox[2] for w in line_words]
            ys = [w.bbox[1] for w in line_words] + [w.bbox[3] for w in line_words]
            line_bbox = [min(xs), min(ys), max(xs), max(ys)] if xs and ys else [0, 0, 0, 0]

            lines.append(OCRLine(
                text=line_text,
                normalized_text=self.normalizer.normalize_text(line_text),
                words=line_words,
                bbox=line_bbox,
                confidence=round(line_conf, 4)
            ))

        # 4. Compute average confidence
        conf_scores = [w.confidence for w in words if w.confidence > 0]
        avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else 0.85

        result = OCREngineResult(
            engine=self.name,
            language=lang,
            text=full_text.strip(),
            normalized_text=self.normalizer.normalize_text(full_text),
            words=words,
            lines=lines,
            page_number=1,
            average_confidence=round(avg_conf, 4),
            metadata={"psm": psm, "oem": oem, "num_words": len(words), "num_lines": len(lines)}
        )

        return self.normalizer.normalize_result(result, img_width=img_w, img_height=img_h)
