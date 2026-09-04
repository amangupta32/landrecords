"""Cross-field consistency validator and land area unit converter."""

from typing import Any, Dict, List, Optional, Tuple
from schemas.fields import AreaField, ExtractedFields
from validation.rules import ValidationRuleResult


class CrossFieldValidator:
    """Validates cross-field relational consistency and standardizes area measurements."""

    # Unit to Square Meters conversion factors
    UNIT_TO_SQM = {
        "hectare": 10000.0,
        "acre": 4046.8564,
        "bigha": 2529.285,
        "biswa": 126.464,
        "sq_meter": 1.0,
        "guntha": 101.17,
    }

    def standardize_area_to_sqm(self, area: AreaField) -> Tuple[Optional[float], Optional[str]]:
        """Convert any land area unit to standard Square Meters."""
        if area.value is None or area.value <= 0:
            return None, "Area value is missing or invalid"
        
        unit_key = (area.unit or "acre").lower().replace(" ", "_")
        factor = self.UNIT_TO_SQM.get(unit_key)
        
        if factor is not None:
            sqm_val = round(area.value * factor, 2)
            return sqm_val, None
        
        return None, f"Unsupported area unit: '{area.unit}'"

    def validate_cross_field(self, fields: ExtractedFields) -> List[ValidationRuleResult]:
        """Run cross-field relational validation checks."""
        results: List[ValidationRuleResult] = []

        # 1. Area standardizability check
        sqm, err = self.standardize_area_to_sqm(fields.land_area)
        if sqm is not None:
            results.append(ValidationRuleResult(
                rule_name="area_unit_standardization",
                field_name="land_area",
                is_valid=True,
                score=1.0,
                message=f"Area converted to standard SI: {sqm:,.2f} sq meters ({fields.land_area.value} {fields.land_area.unit})",
                level="INFO"
            ))
        else:
            results.append(ValidationRuleResult(
                rule_name="area_unit_standardization",
                field_name="land_area",
                is_valid=False,
                score=0.4,
                message=f"Area could not be standardized to Sq Meters: {err}",
                level="WARNING"
            ))

        # 2. Relationship between owners and Khasra plots
        has_khasra = bool(fields.khasra_numbers)
        has_owners = bool(fields.owner_names)
        if has_khasra and has_owners:
            results.append(ValidationRuleResult(
                rule_name="plot_ownership_link",
                field_name="owner_names",
                is_valid=True,
                score=1.0,
                message="Khasra plot parcel successfully linked to tenure holder(s)",
                level="INFO"
            ))
        else:
            results.append(ValidationRuleResult(
                rule_name="plot_ownership_link",
                field_name="owner_names",
                is_valid=False,
                score=0.3,
                message="Missing either Khasra parcel or Owner name for title linkage",
                level="ERROR"
            ))

        return results
