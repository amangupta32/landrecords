"""OCR Engine Router: Dispatches documents to optimal OCR engines based on quality and availability."""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image

from ocr.base import OCREngine
from ocr.fallback import LandRecordFallbackEngine
from ocr.indic_htr import IndicHTREngine
from ocr.normalizer import OCRNormalizer
from ocr.paddleocr_engine import PaddleOCREngine
from ocr.tesseract import TesseractEngine
from schemas.ocr import OCREngineResult, OCRSummary

logger = logging.getLogger(__name__)


class OCREngineRouter:
    """
    Intelligent router selecting the best available OCR engine based on
    document quality analysis, language preferences, handwritten flags, and system capabilities.
    """

    def __init__(self, normalizer: Optional[OCRNormalizer] = None):
        self.normalizer = normalizer or OCRNormalizer()
        self.engines: Dict[str, OCREngine] = {
            "tesseract": TesseractEngine(normalizer=self.normalizer),
            "paddleocr": PaddleOCREngine(normalizer=self.normalizer),
            "indic_htr": IndicHTREngine(normalizer=self.normalizer),
            "fallback": LandRecordFallbackEngine(normalizer=self.normalizer),
        }

    def get_available_engines(self) -> List[str]:
        """Return list of engine names currently functional on the host."""
        return [name for name, engine in self.engines.items() if engine.is_available()]

    def select_engine(
        self,
        preferred_engine: Optional[str] = None,
        is_handwritten: bool = False,
        quality_score: Optional[float] = None,
        quality_grade: Optional[str] = None
    ) -> OCREngine:
        """
        Select engine following priority and availability logic.
        """
        if preferred_engine and preferred_engine in self.engines:
            engine = self.engines[preferred_engine]
            if engine.is_available():
                return engine

        # Handwritten documents route to Indic HTR
        if is_handwritten:
            indic_engine = self.engines["indic_htr"]
            if indic_engine.is_available():
                return indic_engine

        # Try PaddleOCR first for high/medium quality
        paddle = self.engines["paddleocr"]
        if paddle.is_available():
            return paddle

        # Try Tesseract
        tesseract = self.engines["tesseract"]
        if tesseract.is_available():
            return tesseract

        # Default to Fallback Engine
        return self.engines["fallback"]

    def recognize(
        self,
        image: Union[np.ndarray, Image.Image, str],
        preferred_engine: Optional[str] = None,
        language: Optional[str] = None,
        is_handwritten: bool = False,
        quality_score: Optional[float] = None,
        quality_grade: Optional[str] = None,
        **kwargs: Any
    ) -> Tuple[OCREngineResult, OCRSummary]:
        """
        Execute recognition through the selected engine with fallback protection.
        """
        selected = self.select_engine(
            preferred_engine=preferred_engine,
            is_handwritten=is_handwritten,
            quality_score=quality_score,
            quality_grade=quality_grade
        )

        executed_engines = [selected.name]
        fallback_used = False

        try:
            result = selected.recognize(image, language=language, **kwargs)
        except Exception as e:
            logger.warning(f"Engine {selected.name} failed with error: {e}. Switching to fallback engine.")
            fallback_engine = self.engines["fallback"]
            result = fallback_engine.recognize(image, language=language, **kwargs)
            executed_engines.append("fallback")
            fallback_used = True

        summary = OCRSummary(
            primary_engine=result.engine,
            fallback_used=fallback_used or result.engine == "fallback",
            average_confidence=result.average_confidence,
            engines_executed=executed_engines,
            agreement_score=None
        )

        return result, summary
