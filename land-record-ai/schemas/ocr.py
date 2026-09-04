"""Pydantic schemas for standardized OCR outputs across all engines."""

from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Normalized bounding box coordinates [x_min, y_min, x_max, y_max]."""
    x_min: int = Field(..., ge=0)
    y_min: int = Field(..., ge=0)
    x_max: int = Field(..., ge=0)
    y_max: int = Field(..., ge=0)

    @property
    def as_list(self) -> List[int]:
        return [self.x_min, self.y_min, self.x_max, self.y_max]

    @property
    def center(self) -> Tuple[float, float]:
        return ((self.x_min + self.x_max) / 2.0, (self.y_min + self.y_max) / 2.0)

    @property
    def width(self) -> int:
        return max(0, self.x_max - self.x_min)

    @property
    def height(self) -> int:
        return max(0, self.y_max - self.y_min)


class OCRWord(BaseModel):
    """Single OCR-recognized word with spatial coordinates and confidence."""
    text: str = Field(..., description="Recognized word text")
    normalized_text: Optional[str] = Field(default=None, description="Indic-numeral normalized text")
    bbox: List[int] = Field(..., description="[x_min, y_min, x_max, y_max]")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")


class OCRLine(BaseModel):
    """Line of recognized words."""
    text: str = Field(..., description="Full line text")
    normalized_text: Optional[str] = Field(default=None)
    words: List[OCRWord] = Field(default_factory=list)
    bbox: Optional[List[int]] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class OCREngineResult(BaseModel):
    """Normalized standard output from any OCR engine (Tesseract, PaddleOCR, Indic HTR, Fallback)."""
    engine: str = Field(..., description="Engine name: 'tesseract', 'paddleocr', 'indic_htr', 'fallback'")
    language: str = Field(default="hin+eng", description="Language code used")
    text: str = Field(..., description="Full concatenated recognized text")
    normalized_text: Optional[str] = Field(default=None, description="Text after Indic numeral & symbol normalization")
    words: List[OCRWord] = Field(default_factory=list, description="Word tokens with bounding boxes")
    lines: List[OCRLine] = Field(default_factory=list, description="Line tokens")
    page_number: int = Field(default=1, ge=1)
    average_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OCRSummary(BaseModel):
    """Summary of OCR performance across document."""
    primary_engine: str = Field(default="paddleocr", description="Primary OCR engine used")
    fallback_used: bool = Field(default=False, description="Whether domain fallback was triggered")
    average_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    engines_executed: List[str] = Field(default_factory=list)
    agreement_score: Optional[float] = Field(default=None, description="Ensemble agreement score (0-1)")
