"""Final output schemas and explainable confidence representations."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from schemas.document import DocumentQuality
from schemas.fields import ExtractedFields
from schemas.ocr import OCRSummary


class ConfidenceTier(str, Enum):
    VERY_HIGH = "VERY_HIGH"  # 0.90 - 1.00
    HIGH = "HIGH"            # 0.75 - 0.89
    MEDIUM = "MEDIUM"        # 0.50 - 0.74
    LOW = "LOW"              # 0.00 - 0.49


class ComponentConfidenceScores(BaseModel):
    """Breakdown of individual 4-component scores."""
    ocr: float = Field(default=0.0, ge=0.0, le=1.0, description="OCR character/word confidence (40%)")
    extraction: float = Field(default=0.0, ge=0.0, le=1.0, description="Hybrid NLP extraction & proximity (30%)")
    validation: float = Field(default=0.0, ge=0.0, le=1.0, description="Format & geographic validation (20%)")
    context: float = Field(default=0.0, ge=0.0, le=1.0, description="Domain context window match (10%)")


class FieldConfidenceDetail(BaseModel):
    """Explainable confidence score for an individual field."""
    score: float = Field(..., ge=0.0, le=1.0)
    tier: ConfidenceTier = Field(default=ConfidenceTier.LOW)
    components: ComponentConfidenceScores = Field(default_factory=ComponentConfidenceScores)
    reasons: List[str] = Field(default_factory=list, description="Human-readable reasons for this score")


class DocumentConfidence(BaseModel):
    """Document-level overall confidence score and tier."""
    overall: float = Field(..., ge=0.0, le=1.0)
    tier: ConfidenceTier = Field(default=ConfidenceTier.LOW)


class DocumentProcessingOutput(BaseModel):
    """Final canonical output JSON schema for Land Record AI matching Section 23."""
    document_id: str = Field(..., description="Unique document ID")
    pages: int = Field(default=1, ge=1, description="Total pages processed")
    document_quality: DocumentQuality = Field(..., description="Quality analysis and blur score")
    ocr: OCRSummary = Field(..., description="OCR engines summary and confidence")
    fields: ExtractedFields = Field(..., description="Structured extracted land record fields")
    confidence: DocumentConfidence = Field(..., description="Overall document confidence and tier")
    explanations: List[str] = Field(default_factory=list, description="Top-level human-readable explanations")
    needs_human_review: bool = Field(default=False, description="True if any crucial field is low confidence")
    field_confidences: Dict[str, FieldConfidenceDetail] = Field(
        default_factory=dict,
        description="Per-field explainable confidence details"
    )
    processing_time_ms: Optional[float] = Field(default=None, description="Total pipeline latency in milliseconds")
