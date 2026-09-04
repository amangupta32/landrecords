"""OCR module: engine abstractions, Tesseract, PaddleOCR, Indic HTR, Fallback, Router, and Ensemble."""

from ocr.base import OCREngine
from ocr.normalizer import OCRNormalizer
from ocr.tesseract import TesseractEngine
from ocr.paddleocr_engine import PaddleOCREngine
from ocr.indic_htr import IndicHTREngine
from ocr.fallback import LandRecordFallbackEngine
from ocr.router import OCREngineRouter
from ocr.ensemble import OCREnsemble

__all__ = [
    "OCREngine",
    "OCRNormalizer",
    "TesseractEngine",
    "PaddleOCREngine",
    "IndicHTREngine",
    "LandRecordFallbackEngine",
    "OCREngineRouter",
    "OCREnsemble",
]
