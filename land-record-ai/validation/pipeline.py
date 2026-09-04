"""Validation Pipeline: Coordinates format, geographic, and cross-field validation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from schemas.fields import ExtractedFields
from validation.cross_field import CrossFieldValidator
from validation.geographic import GeographicHierarchyValidator
from validation.rules import FormatValidator, ValidationRuleResult


class ValidationReport(BaseModel):
    """Consolidated output of the validation pipeline."""
    validation_score: float = Field(default=1.0, ge=0.0, le=1.0)
    is_valid: bool = True
    rule_results: List[ValidationRuleResult] = Field(default_factory=list)
    field_scores: Dict[str, float] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ValidationPipeline:
    """
    Coordinates all validation rules across format, geographic consistency,
    and cross-field business logic.
    """

    def __init__(self, state_rules_dir: Optional[str] = None):
        self.format_validator = FormatValidator()
        self.geographic_validator = GeographicHierarchyValidator(state_rules_dir=state_rules_dir)
        self.cross_field_validator = CrossFieldValidator()

    def validate(self, fields: ExtractedFields) -> ValidationReport:
        """Execute full validation suite on extracted fields."""
        all_results: List[ValidationRuleResult] = []

        # 1. Format & field checks
        all_results.extend(self.format_validator.validate_khasra(fields.khasra_numbers))
        all_results.extend(self.format_validator.validate_khata(fields.khata_numbers))
        all_results.extend(self.format_validator.validate_land_area(fields.land_area))
        all_results.extend(self.format_validator.validate_owners(fields.owner_names))
        all_results.extend(self.format_validator.validate_date(fields.record_date))

        # 2. Geographic checks
        all_results.extend(self.geographic_validator.validate_hierarchy(fields.location))

        # 3. Cross-field checks
        all_results.extend(self.cross_field_validator.validate_cross_field(fields))

        # 4. Compute per-field and overall scores
        field_scores: Dict[str, List[float]] = {}
        warnings: List[str] = []
        errors: List[str] = []

        for r in all_results:
            field_scores.setdefault(r.field_name, []).append(r.score)
            if r.level == "WARNING":
                warnings.append(r.message)
            elif r.level == "ERROR":
                errors.append(r.message)

        avg_field_scores = {
            fn: round(sum(scores) / len(scores), 4) for fn, scores in field_scores.items()
        }

        all_scores = [r.score for r in all_results]
        overall_score = round(sum(all_scores) / len(all_scores), 4) if all_scores else 1.0

        is_valid = len(errors) == 0

        return ValidationReport(
            validation_score=overall_score,
            is_valid=is_valid,
            rule_results=all_results,
            field_scores=avg_field_scores,
            warnings=warnings,
            errors=errors
        )
