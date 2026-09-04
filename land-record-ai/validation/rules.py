"""Rule-based and format validation for extracted land record fields."""

from datetime import datetime
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from schemas.fields import AreaField, DateField, ExtractedFields, KhasraField, KhataField, OwnerField


class ValidationRuleResult(BaseModel):
    """Result of an individual validation rule check."""
    rule_name: str
    field_name: str
    is_valid: bool
    score: float = Field(default=1.0, ge=0.0, le=1.0)
    message: str = ""
    level: str = "INFO"  # "INFO", "WARNING", "ERROR"


class FormatValidator:
    """Validates formats, numeric ranges, mandatory fields, and dates for land records."""

    def validate_khasra(self, khasra_list: List[KhasraField]) -> List[ValidationRuleResult]:
        results = []
        if not khasra_list:
            results.append(ValidationRuleResult(
                rule_name="mandatory_khasra",
                field_name="khasra_numbers",
                is_valid=False,
                score=0.0,
                message="Mandatory field Khasra/Survey number is missing",
                level="ERROR"
            ))
            return results

        for k in khasra_list:
            # Pattern: digits, slashes, optional alphanumeric sub-division
            is_valid_format = bool(re.match(r'^[0-9]+(?:[\/\-][0-9A-Za-z\u0900-\u097F]+)*(?:\s*[क-हA-Za-z])?$', k.value))
            results.append(ValidationRuleResult(
                rule_name="khasra_format",
                field_name="khasra_numbers",
                is_valid=is_valid_format,
                score=1.0 if is_valid_format else 0.4,
                message=f"Khasra number '{k.value}' format is {'valid' if is_valid_format else 'atypical'}",
                level="INFO" if is_valid_format else "WARNING"
            ))
        return results

    def validate_khata(self, khata_list: List[KhataField]) -> List[ValidationRuleResult]:
        results = []
        if not khata_list:
            results.append(ValidationRuleResult(
                rule_name="mandatory_khata",
                field_name="khata_numbers",
                is_valid=True,
                score=0.7,
                message="Khata number not specified in document",
                level="INFO"
            ))
            return results

        for k in khata_list:
            is_valid_format = bool(re.match(r'^[0-9]+(?:[\/\-][0-9]+)?$', k.value))
            results.append(ValidationRuleResult(
                rule_name="khata_format",
                field_name="khata_numbers",
                is_valid=is_valid_format,
                score=1.0 if is_valid_format else 0.5,
                message=f"Khata number '{k.value}' format is {'valid' if is_valid_format else 'irregular'}",
                level="INFO" if is_valid_format else "WARNING"
            ))
        return results

    def validate_land_area(self, area: AreaField) -> List[ValidationRuleResult]:
        results = []
        if area.value is None or area.value <= 0:
            results.append(ValidationRuleResult(
                rule_name="area_positive_nonzero",
                field_name="land_area",
                is_valid=False,
                score=0.0,
                message="Land area value must be a positive non-zero number",
                level="ERROR"
            ))
        elif area.value > 50000:
            results.append(ValidationRuleResult(
                rule_name="area_plausible_bounds",
                field_name="land_area",
                is_valid=False,
                score=0.4,
                message=f"Extracted land area {area.value} exceeds typical plot bounds (> 50,000 units)",
                level="WARNING"
            ))
        else:
            results.append(ValidationRuleResult(
                rule_name="area_positive_nonzero",
                field_name="land_area",
                is_valid=True,
                score=1.0,
                message=f"Land area {area.value} {area.unit or ''} is within valid bounds",
                level="INFO"
            ))
        return results

    def validate_owners(self, owners: List[OwnerField]) -> List[ValidationRuleResult]:
        results = []
        if not owners:
            results.append(ValidationRuleResult(
                rule_name="mandatory_owner",
                field_name="owner_names",
                is_valid=False,
                score=0.0,
                message="Mandatory field Owner/Khatedar name is missing",
                level="ERROR"
            ))
            return results

        for o in owners:
            has_name = bool(o.name and len(o.name.strip()) >= 2)
            results.append(ValidationRuleResult(
                rule_name="owner_name_validity",
                field_name="owner_names",
                is_valid=has_name,
                score=1.0 if has_name else 0.3,
                message=f"Owner name '{o.name}' {'is valid' if has_name else 'is too short or invalid'}",
                level="INFO" if has_name else "WARNING"
            ))
        return results

    def validate_date(self, date_field: Optional[DateField]) -> List[ValidationRuleResult]:
        results = []
        if not date_field or not date_field.iso_date:
            results.append(ValidationRuleResult(
                rule_name="record_date_presence",
                field_name="record_date",
                is_valid=True,
                score=0.8,
                message="Record date not explicitly stated",
                level="INFO"
            ))
            return results

        try:
            dt = datetime.strptime(date_field.iso_date, "%Y-%m-%d")
            now = datetime.now()
            if dt > now:
                results.append(ValidationRuleResult(
                    rule_name="date_not_future",
                    field_name="record_date",
                    is_valid=False,
                    score=0.3,
                    message=f"Record date '{date_field.iso_date}' is in the future",
                    level="ERROR"
                ))
            elif dt.year < 1850:
                results.append(ValidationRuleResult(
                    rule_name="date_historical_bounds",
                    field_name="record_date",
                    is_valid=False,
                    score=0.4,
                    message=f"Record date '{date_field.iso_date}' predates modern revenue records (< 1850)",
                    level="WARNING"
                ))
            else:
                results.append(ValidationRuleResult(
                    rule_name="date_validity",
                    field_name="record_date",
                    is_valid=True,
                    score=1.0,
                    message=f"Record date '{date_field.iso_date}' is valid",
                    level="INFO"
                ))
        except ValueError:
            results.append(ValidationRuleResult(
                rule_name="date_parse_error",
                field_name="record_date",
                is_valid=False,
                score=0.2,
                message=f"Invalid ISO date format: '{date_field.iso_date}'",
                level="ERROR"
            ))

        return results
