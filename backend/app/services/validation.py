from typing import Dict, Any, List

class ValidationEngine:
    MASTER_LOCATION_HIERARCHY = {
        "Uttar Pradesh": {
            "Rampur District": {
                "Rampur Tehsil": ["Rampur", "Chandpur", "Bilaspur", "Shahabad"],
                "Suar Tehsil": ["Suar", "Tanda", "Kalyanpur"]
            },
            "Lucknow District": {
                "Sadar Tehsil": ["Malihabad", "Chinhat", "Kakori"]
            }
        },
        "Madhya Pradesh": {
            "Indore District": {
                "Indore Tehsil": ["Rau", "Mhow", "Kanadia"]
            }
        }
    }

    UNIT_CONVERSIONS_TO_SQM = {
        "Acres": 4046.86,
        "Hectares": 10000.0,
        "Bigha": 2529.3,
        "Guntha": 101.17,
        "Sq Meters": 1.0
    }

    def validate_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        validations = []
        overall_valid = True

        # 1. Required Fields Check
        required_fields = ["owner_name", "khasra_number", "village"]
        for field in required_fields:
            val = record_data.get(field)
            if not val or val == "Unknown Owner":
                validations.append({
                    "rule_name": "REQUIRED_FIELD_CHECK",
                    "field_name": field,
                    "is_valid": False,
                    "severity": "Error",
                    "message": f"Mandatory field '{field}' is missing or incomplete."
                })
                overall_valid = False
            else:
                validations.append({
                    "rule_name": "REQUIRED_FIELD_CHECK",
                    "field_name": field,
                    "is_valid": True,
                    "severity": "Info",
                    "message": f"Mandatory field '{field}' present."
                })

        # 2. Area Non-Zero & Unit Normalization
        land_area = record_data.get("land_area", 0.0)
        unit = record_data.get("land_area_unit", "Acres")
        
        if land_area <= 0:
            validations.append({
                "rule_name": "AREA_NON_ZERO",
                "field_name": "land_area",
                "is_valid": False,
                "severity": "Error",
                "message": "Land area must be greater than zero."
            })
            overall_valid = False
            area_sqm = 0.0
        else:
            conv_factor = self.UNIT_CONVERSIONS_TO_SQM.get(unit, 4046.86)
            area_sqm = round(land_area * conv_factor, 1)
            validations.append({
                "rule_name": "AREA_NORMALIZATION",
                "field_name": "land_area",
                "is_valid": True,
                "severity": "Info",
                "message": f"Land area valid: {land_area} {unit} equals {area_sqm} sq. meters."
            })

        # 3. Location Hierarchy Verification
        village = record_data.get("village", "Rampur")
        tehsil = record_data.get("tehsil", "Rampur Tehsil")
        district = record_data.get("district", "Rampur District")
        state = record_data.get("state", "Uttar Pradesh")

        state_data = self.MASTER_LOCATION_HIERARCHY.get(state, {})
        dist_data = state_data.get(district, {})
        valid_villages = dist_data.get(tehsil, [])

        if valid_villages and village not in valid_villages:
            validations.append({
                "rule_name": "LOCATION_HIERARCHY",
                "field_name": "village",
                "is_valid": False,
                "severity": "Warning",
                "message": f"Village '{village}' is not indexed under Tehsil '{tehsil}' in {district}, {state}."
            })
        else:
            validations.append({
                "rule_name": "LOCATION_HIERARCHY",
                "field_name": "village",
                "is_valid": True,
                "severity": "Info",
                "message": f"Location hierarchy verified: Village '{village}' -> Tehsil '{tehsil}' -> District '{district}'."
            })

        return {
            "overall_valid": overall_valid,
            "area_sq_meters": area_sqm,
            "validations": validations
        }

validation_engine = ValidationEngine()
