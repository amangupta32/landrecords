"""Abstract Base Class for OCR engines in the Land Record AI pipeline."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import numpy as np
from PIL import Image

from schemas.ocr import OCREngineResult


class OCREngine(ABC):
    """Standard interface for all OCR engines (Tesseract, PaddleOCR, Indic HTR, Fallback)."""

    def __init__(self, name: str, default_language: str = "hin+eng"):
        self.name = name
        self.default_language = default_language

    @abstractmethod
    def recognize(
        self,
        image: Union[np.ndarray, Image.Image, str],
        language: Optional[str] = None,
        **kwargs: Any
    ) -> OCREngineResult:
        """
        Recognize text and word bounding boxes from an input image.

        Args:
            image: Document image as numpy array (BGR/Grayscale), PIL Image, or file path.
            language: Target OCR language code (e.g. 'hin', 'eng', 'hin+eng', 'mar').
            **kwargs: Engine-specific parameters.

        Returns:
            OCREngineResult schema with text, words, lines, bboxes, and confidences.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if required binary dependencies and packages are installed and available."""
        pass
