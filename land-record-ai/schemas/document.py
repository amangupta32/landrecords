"""Document input, quality, and preprocessing Pydantic schemas."""

from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field, ConfigDict
import numpy as np


class DocumentQuality(BaseModel):
    """Quality analysis metrics calculated before and during preprocessing."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    laplacian_variance: float = Field(..., description="Variance of Laplacian used for blur scoring")
    quality: str = Field(..., description="Quality classification: 'poor', 'acceptable', or 'good'")
    brightness: float = Field(default=0.0, description="Mean grayscale intensity (0-255)")
    contrast: float = Field(default=0.0, description="Standard deviation of pixel intensities")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    dpi: Optional[int] = Field(default=None, description="Extracted or estimated DPI")
    is_blurry: bool = Field(default=False, description="True if blur score is below threshold")


class DeskewMetadata(BaseModel):
    """Deskewing transformation metrics and confidence."""
    rotation_angle: float = Field(default=0.0, description="Estimated skew angle in degrees")
    deskew_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence of line detection")
    was_rotated: bool = Field(default=False, description="Whether rotation was actually applied")
    method: str = Field(default="hough_lines", description="Method used for deskew angle calculation")


class PreprocessingMetadata(BaseModel):
    """Detailed metadata describing all preprocessing transformations executed."""
    processing_steps: List[str] = Field(default_factory=list, description="List of applied filter steps")
    rotation_angle: float = Field(default=0.0, description="Rotation angle applied in degrees")
    deskew_confidence: float = Field(default=0.0, description="Deskew line detection confidence")
    blur_score: float = Field(default=0.0, description="Laplacian variance blur score")
    quality: str = Field(default="unknown", description="Quality classification")
    original_shape: List[int] = Field(default_factory=list, description="[Height, Width, Channels]")
    final_shape: List[int] = Field(default_factory=list, description="[Height, Width]")
    duration_ms: float = Field(default=0.0, description="Processing duration in milliseconds")


class PreprocessingResult(BaseModel):
    """Complete typed result returned by PreprocessingPipeline.process()."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    processed_image: Any = Field(..., description="Final OCR-ready image (numpy ndarray or bytes)")
    blur_score: float = Field(..., description="Laplacian blur score")
    quality: str = Field(..., description="Quality grade ('poor', 'acceptable', 'good')")
    rotation_angle: float = Field(default=0.0, description="Estimated/applied rotation angle")
    deskew_confidence: float = Field(default=0.0, description="Confidence of the deskew angle")
    quality_analysis: DocumentQuality = Field(..., description="Full quality analysis metrics")
    deskew_details: DeskewMetadata = Field(..., description="Deskew details")
    metadata: PreprocessingMetadata = Field(..., description="Processing pipeline metadata")
    variants: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Named intermediate images: original, grayscale, denoised, clahe, deskewed, otsu"
    )


class PageInput(BaseModel):
    """Single page representation within a document."""
    page_number: int = Field(default=1, ge=1)
    has_selectable_text: bool = Field(default=False)
    raw_text: Optional[str] = None
    image_bytes: Optional[bytes] = None


class DocumentInput(BaseModel):
    """Input document container supporting multi-page PDF and single images."""
    document_id: str = Field(..., description="Unique document identifier")
    file_path: Optional[str] = None
    file_type: str = Field(default="image", description="Document type: 'pdf', 'jpg', 'png', 'tiff'")
    total_pages: int = Field(default=1, ge=1)
    pages: List[PageInput] = Field(default_factory=list)
