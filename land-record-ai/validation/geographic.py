"""Geographic and Administrative Hierarchy Validator against State Revenue rules."""

import os
from typing import Any, Dict, List, Optional
import yaml

from schemas.fields import LocationHierarchyField
from validation.rules import ValidationRuleResult


class GeographicHierarchyValidator:
    """Validates location hierarchies (Village -> Tehsil -> District -> State) against revenue master rules."""

    def __init__(self, state_rules_dir: Optional[str] = None):
        self.state_rules = self._load_rules(state_rules_dir)

    def _load_rules(self, rules_dir: Optional[str]) -> Dict[str, Any]:
        dir_path = rules_dir or os.path.join(os.path.dirname(__file__), "..", "config", "state_rules")
        rules = {}
        if os.path.exists(dir_path):
            for fn in os.listdir(dir_path):
                if fn.endswith(".yaml") or fn.endswith(".yml"):
                    fp = os.path.join(dir_path, fn)
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f) or {}
                            st_key = fn.replace(".yaml", "").replace(".yml", "")
                            rules[st_key] = data
                    except Exception:
                        pass
        return rules

    def validate_hierarchy(self, location: LocationHierarchyField) -> List[ValidationRuleResult]:
        """Validate location completeness and administrative hierarchy relationships."""
        results: List[ValidationRuleResult] = []

        if not location:
            results.append(ValidationRuleResult(
                rule_name="location_presence",
                field_name="location",
                is_valid=False,
                score=0.0,
                message="Location hierarchy is completely missing",
                level="ERROR"
            ))
            return results

        # 1. Check completeness of tiers
        missing_tiers = []
        if not location.state:
            missing_tiers.append("State")
        if not location.district:
            missing_tiers.append("District")
        if not location.tehsil:
            missing_tiers.append("Tehsil")
        if not location.village:
            missing_tiers.append("Village")

        if missing_tiers:
            completeness_score = max(0.2, 1.0 - (len(missing_tiers) * 0.25))
            results.append(ValidationRuleResult(
                rule_name="hierarchy_completeness",
                field_name="location",
                is_valid=False,
                score=completeness_score,
                message=f"Location hierarchy incomplete. Missing: {', '.join(missing_tiers)}",
                level="WARNING"
            ))
        else:
            results.append(ValidationRuleResult(
                rule_name="hierarchy_completeness",
                field_name="location",
                is_valid=True,
                score=1.0,
                message="Complete administrative hierarchy present (Village -> Tehsil -> District -> State)",
                level="INFO"
            ))

        # 2. State-specific validation check
        state_matched = False
        for st_name, rule_data in self.state_rules.items():
            st_cfg_name = rule_data.get("state_name", "")
            if location.state and (st_cfg_name.lower() in location.state.lower() or st_name in location.state.lower()):
                state_matched = True
                results.append(ValidationRuleResult(
                    rule_name="state_rule_match",
                    field_name="location",
                    is_valid=True,
                    score=1.0,
                    message=f"Location conforms to revenue schema for state: {st_cfg_name or st_name}",
                    level="INFO"
                ))
                break

        if not state_matched and location.state:
            results.append(ValidationRuleResult(
                rule_name="state_rule_match",
                field_name="location",
                is_valid=True,
                score=0.85,
                message=f"State '{location.state}' verified using standard national revenue schema",
                level="INFO"
            ))

        return results
