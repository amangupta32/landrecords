"""Pydantic models for extracted Land Record domain fields."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FieldCandidate(BaseModel):
    """Represents an extraction candidate scored by the hybrid NLP engine."""
    value: str = Field(..., description="Extracted candidate string")
    normalized_value: Optional[str] = Field(default=None)
    ocr_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    keyword_proximity: float = Field(default=0.0, ge=0.0, le=1.0)
    regex_validity: float = Field(default=0.0, ge=0.0, le=1.0)
    context_match: float = Field(default=0.0, ge=0.0, le=1.0)
    combined_score: float = Field(default=0.0, ge=0.0, le=1.0)
    source_engine: str = Field(default="primary")
    bbox: Optional[List[int]] = None
    page_number: int = Field(default=1)


class OwnerField(BaseModel):
    """Owner / Khatedar representation with relationship extraction."""
    name: str = Field(..., description="Name of the owner/khatedar")
    relation_type: Optional[str] = Field(default=None, description="e.g., S/O, D/O, W/O, पुत्र, पिता")
    relation_name: Optional[str] = Field(default=None, description="Father/Husband name if present")
    raw_text: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tier: str = Field(default="LOW")
    bbox: Optional[List[int]] = None


class KhasraField(BaseModel):
    """Khasra / Survey / Plot number."""
    value: str = Field(..., description="Khasra or Survey plot identifier (e.g. 123, 123/1)")
    raw_text: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tier: str = Field(default="LOW")
    bbox: Optional[List[int]] = None


class KhataField(BaseModel):
    """Khata / Khatauni / Account number."""
    value: str = Field(..., description="Khata / Khatauni account number")
    raw_text: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tier: str = Field(default="LOW")
    bbox: Optional[List[int]] = None


class AreaField(BaseModel):
    """Land area with value, unit, and raw text."""
    value: Optional[float] = Field(default=None, description="Parsed numeric area value")
    unit: Optional[str] = Field(default=None, description="Identified unit: hectare, acre, bigha, biswa, sq_meter")
    raw_text: Optional[str] = Field(default=None, description="Original raw text from document")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tier: str = Field(default="LOW")
    bbox: Optional[List[int]] = None


class LocationHierarchyField(BaseModel):
    """Strict administrative location hierarchy."""
    village: Optional[str] = Field(default=None, description="Village / Gram name")
    tehsil: Optional[str] = Field(default=None, description="Tehsil / Taluka name")
    district: Optional[str] = Field(default=None, description="District / Zila name")
    state: Optional[str] = Field(default=None, description="State / Pradesh name")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tier: str = Field(default="LOW")
    is_valid_hierarchy: Optional[bool] = Field(default=None, description="True if validated against state rules")


class MutationField(BaseModel):
    """Mutation / Dakhil Kharij / Intakaal reference."""
    mutation_number: Optional[str] = Field(default=None, description="Mutation order/entry number")
    raw_text: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tier: str = Field(default="LOW")
    bbox: Optional[List[int]] = None


class DateField(BaseModel):
    """Record / Order date."""
    iso_date: Optional[str] = Field(default=None, description="Normalized ISO date (YYYY-MM-DD)")
    raw_date: Optional[str] = Field(default=None, description="Raw date string from document")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tier: str = Field(default="LOW")
    bbox: Optional[List[int]] = None


class ExtractedFields(BaseModel):
    """Consolidated container for all extracted fields matching Section 23 schema."""
    owner_names: List[OwnerField] = Field(default_factory=list)
    khasra_numbers: List[KhasraField] = Field(default_factory=list)
    khata_numbers: List[KhataField] = Field(default_factory=list)
    land_area: AreaField = Field(default_factory=AreaField)
    location: LocationHierarchyField = Field(default_factory=LocationHierarchyField)
    mutation_reference: Optional[MutationField] = None
    record_date: Optional[DateField] = None
