"""Extraction Pipeline: Coordinates all field extractors on OCR outputs."""

from typing import Any, Dict, List, Optional
from extraction.context_extractor import ContextWindowExtractor
from extraction.location_extractor import LocationHierarchyExtractor
from extraction.owner_extractor import OwnerFieldExtractor
from extraction.regex_extractor import RegexFieldExtractor
from schemas.fields import AreaField, ExtractedFields, LocationHierarchyField
from schemas.ocr import OCREngineResult


class ExtractionPipeline:
    """
    Coordinates multi-strategy extraction over OCR engine results to construct
    canonical typed ExtractedFields model.
    """

    def __init__(
        self,
        fields_config_path: Optional[str] = None,
        state_rules_dir: Optional[str] = None
    ):
        self.regex_extractor = RegexFieldExtractor(fields_config_path=fields_config_path)
        self.owner_extractor = OwnerFieldExtractor(fields_config_path=fields_config_path)
        self.location_extractor = LocationHierarchyExtractor(state_rules_dir=state_rules_dir)
        self.context_extractor = ContextWindowExtractor()

    def extract(self, ocr_result: OCREngineResult) -> ExtractedFields:
        """
        Extract all land record entities from OCR results.
        """
        text = ocr_result.normalized_text or ocr_result.text
        words = ocr_result.words

        # 1. Khasra Numbers
        khasra_list = self.regex_extractor.extract_khasra_numbers(text, words=words)

        # 2. Khata Numbers
        khata_list = self.regex_extractor.extract_khata_numbers(text, words=words)

        # 3. Land Area
        land_area = self.regex_extractor.extract_land_area(text, words=words)

        # 4. Owners & Relationships
        owners = self.owner_extractor.extract_owners(text, words=words)

        # 5. Location Hierarchy
        location = self.location_extractor.extract_hierarchy(text, words=words)

        # 6. Mutation Reference
        mutation = self.regex_extractor.extract_mutation_reference(text, words=words)

        # 7. Record Date
        record_date = self.regex_extractor.extract_record_date(text, words=words)

        return ExtractedFields(
            owner_names=owners,
            khasra_numbers=khasra_list,
            khata_numbers=khata_list,
            land_area=land_area,
            location=location,
            mutation_reference=mutation,
            record_date=record_date
        )
