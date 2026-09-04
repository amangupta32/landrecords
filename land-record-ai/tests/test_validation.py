"""Unit tests for Validation engine modules and pipeline."""

import pytest
from schemas.fields import AreaField, DateField, ExtractedFields, KhasraField, KhataField, LocationHierarchyField, OwnerField
from validation.cross_field import CrossFieldValidator
from validation.geographic import GeographicHierarchyValidator
from validation.pipeline import ValidationPipeline, ValidationReport
from validation.rules import FormatValidator


class TestFormatValidator:
    @pytest.fixture
    def validator(self):
        return FormatValidator()

    def test_valid_khasra(self, validator):
        khasra = [KhasraField(value="245/1")]
        results = validator.validate_khasra(khasra)
        assert len(results) == 1
        assert results[0].is_valid is True
        assert results[0].score == 1.0

    def test_missing_khasra(self, validator):
        results = validator.validate_khasra([])
        assert len(results) == 1
        assert results[0].is_valid is False
        assert results[0].level == "ERROR"

    def test_land_area_positive_nonzero(self, validator):
        area = AreaField(value=4.25, unit="acre")
        results = validator.validate_land_area(area)
        assert results[0].is_valid is True
        assert results[0].score == 1.0

    def test_land_area_zero_or_negative(self, validator):
        area = AreaField(value=0.0, unit="acre")
        results = validator.validate_land_area(area)
        assert results[0].is_valid is False
        assert results[0].level == "ERROR"

    def test_future_date_rejected(self, validator):
        date_field = DateField(iso_date="2099-01-01")
        results = validator.validate_date(date_field)
        assert results[0].is_valid is False
        assert results[0].level == "ERROR"


class TestGeographicValidator:
    @pytest.fixture
    def validator(self):
        return GeographicHierarchyValidator()

    def test_complete_hierarchy(self, validator):
        loc = LocationHierarchyField(
            village="Rampur",
            tehsil="Rampur Tehsil",
            district="Rampur District",
            state="Uttar Pradesh"
        )
        results = validator.validate_hierarchy(loc)
        completeness = next(r for r in results if r.rule_name == "hierarchy_completeness")
        assert completeness.is_valid is True
        assert completeness.score == 1.0


class TestCrossFieldValidator:
    @pytest.fixture
    def validator(self):
        return CrossFieldValidator()

    def test_hectare_to_sqm_conversion(self, validator):
        area = AreaField(value=2.5, unit="hectare")
        sqm, err = validator.standardize_area_to_sqm(area)
        assert err is None
        assert sqm == 25000.0

    def test_acre_to_sqm_conversion(self, validator):
        area = AreaField(value=1.0, unit="acre")
        sqm, err = validator.standardize_area_to_sqm(area)
        assert err is None
        assert 4040.0 < sqm < 4050.0


class TestValidationPipeline:
    def test_full_pipeline_valid_fields(self):
        fields = ExtractedFields(
            owner_names=[OwnerField(name="Ramesh Kumar Sharma", relation_type="S/O", relation_name="Harish Chandra Sharma")],
            khasra_numbers=[KhasraField(value="245/1")],
            khata_numbers=[KhataField(value="89")],
            land_area=AreaField(value=4.25, unit="acre"),
            location=LocationHierarchyField(
                village="Rampur",
                tehsil="Rampur Tehsil",
                district="Rampur District",
                state="Uttar Pradesh"
            ),
            record_date=DateField(iso_date="2024-01-15")
        )

        pipeline = ValidationPipeline()
        report = pipeline.validate(fields)

        assert isinstance(report, ValidationReport)
        assert report.is_valid is True
        assert report.validation_score >= 0.85
        assert len(report.errors) == 0
        assert "land_area" in report.field_scores
        assert "khasra_numbers" in report.field_scores
