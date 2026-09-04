"""Unit tests for Hybrid NLP Field Extraction modules and pipeline."""

import pytest
from extraction.context_extractor import ContextWindowExtractor
from extraction.location_extractor import LocationHierarchyExtractor
from extraction.owner_extractor import OwnerFieldExtractor
from extraction.pipeline import ExtractionPipeline
from extraction.regex_extractor import RegexFieldExtractor
from ocr.fallback import LandRecordFallbackEngine
from schemas.fields import ExtractedFields
from schemas.ocr import OCRWord


class TestRegexFieldExtractor:
    @pytest.fixture
    def extractor(self):
        return RegexFieldExtractor()

    def test_khasra_extraction(self, extractor):
        text = "खसरा संख्या: 245/1 एवं खाता संख्या: 89"
        khasra = extractor.extract_khasra_numbers(text)
        assert len(khasra) >= 1
        assert khasra[0].value == "245/1"

    def test_khasra_legacy_alphanumeric(self, extractor):
        text = "खसरा संख्या: 312/B"
        khasra = extractor.extract_khasra_numbers(text)
        assert len(khasra) >= 1
        assert "312/B" in [k.value for k in khasra]

    def test_khata_extraction(self, extractor):
        text = "खाता संख्या: 89"
        khata = extractor.extract_khata_numbers(text)
        assert len(khata) >= 1
        assert khata[0].value == "89"

    def test_land_area_hectares(self, extractor):
        text = "क्षेत्रफल: 2.50 हेक्टेयर"
        area = extractor.extract_land_area(text)
        assert area.value == 2.50
        assert area.unit == "hectare"

    def test_land_area_acres(self, extractor):
        text = "कुल क्षेत्रफल: 4.25 एकड़"
        area = extractor.extract_land_area(text)
        assert area.value == 4.25
        assert area.unit == "acre"

    def test_mutation_reference(self, extractor):
        text = "नामांतरण क्रमांक: MUT-2023-882"
        mut = extractor.extract_mutation_reference(text)
        assert mut is not None
        assert mut.mutation_number == "MUT-2023-882"

    def test_record_date_dmy(self, extractor):
        text = "दिनांक: 15/01/2024"
        d = extractor.extract_record_date(text)
        assert d is not None
        assert d.iso_date == "2024-01-15"

    def test_record_date_iso(self, extractor):
        text = "Date: 2023-11-20"
        d = extractor.extract_record_date(text)
        assert d is not None
        assert d.iso_date == "2023-11-20"


class TestOwnerFieldExtractor:
    @pytest.fixture
    def extractor(self):
        return OwnerFieldExtractor()

    def test_owner_name_with_hindi_relation(self, extractor):
        text = "खाता धारक का नाम: रमेश कुमार शर्मा\nपिता का नाम: हरीश चंद्र शर्मा"
        owners = extractor.extract_owners(text)
        assert len(owners) >= 1
        assert "Ramesh Kumar Sharma" in owners[0].name or "रमेश कुमार शर्मा" in owners[0].name
        assert owners[0].relation_name is not None

    def test_owner_bilingual_saledeed(self, extractor):
        text = "क्रेता का नाम: सुरेश कुमार वर्मा (Suresh Kumar Verma)\nपिता का नाम: राम लाल वर्मा (Ram Lal Verma)"
        owners = extractor.extract_owners(text)
        assert len(owners) >= 1
        assert owners[0].name == "Suresh Kumar Verma"
        assert owners[0].relation_type == "S/O"
        assert owners[0].relation_name == "Ram Lal Verma"


class TestLocationHierarchyExtractor:
    @pytest.fixture
    def extractor(self):
        return LocationHierarchyExtractor()

    def test_location_hierarchy_resolution(self, extractor):
        text = """
        ग्राम: रामपुर (Rampur)
        तहसील: रामपुर तहसील (Rampur Tehsil)
        जिला: रामपुर (Rampur District)
        राज्य: उत्तर प्रदेश (Uttar Pradesh)
        """
        loc = extractor.extract_hierarchy(text)
        assert loc.village == "Rampur"
        assert loc.tehsil == "Rampur Tehsil"
        assert loc.district == "Rampur District"
        assert loc.state == "Uttar Pradesh"
        assert loc.is_valid_hierarchy is True


class TestContextWindowExtractor:
    def test_candidate_ranking_by_proximity(self):
        extractor = ContextWindowExtractor()
        words = [
            OCRWord(text="खसरा", bbox=[100, 100, 150, 130], confidence=0.98),
            OCRWord(text="संख्या", bbox=[160, 100, 220, 130], confidence=0.95),
            OCRWord(text="245/1", bbox=[240, 100, 310, 130], confidence=0.97),
            OCRWord(text="1998", bbox=[600, 500, 660, 530], confidence=0.90),
        ]
        candidates = extractor.rank_candidates(
            anchor_keywords=["खसरा"],
            words=words,
            candidate_pattern=r'^[0-9]+(?:\/[0-9]+)?$'
        )
        assert len(candidates) >= 1
        # 245/1 is right next to "खसरा" and should rank top
        assert candidates[0].value == "245/1"
        assert candidates[0].keyword_proximity > 0.8


class TestExtractionPipeline:
    def test_pipeline_on_fallback_ocr(self):
        fallback = LandRecordFallbackEngine()
        ocr_res = fallback.recognize("dummy_path", template_name="jamabandi")

        pipeline = ExtractionPipeline()
        fields = pipeline.extract(ocr_res)

        assert isinstance(fields, ExtractedFields)
        assert len(fields.khasra_numbers) >= 1
        assert fields.khasra_numbers[0].value == "245/1"
        assert len(fields.khata_numbers) >= 1
        assert fields.khata_numbers[0].value == "89"
        assert fields.land_area.value == 4.25
        assert fields.land_area.unit == "acre"
        assert len(fields.owner_names) >= 1
        assert fields.location.village == "Rampur"
        assert fields.mutation_reference is not None
        assert fields.record_date is not None
