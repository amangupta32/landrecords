"""End-to-End Land Record AI Pipeline Orchestrator."""

import os
import time
import uuid
from typing import Any, Dict, List, Optional, Union
import numpy as np
from PIL import Image

from confidence.scorer import ExplainableConfidenceScorer
from extraction.pipeline import ExtractionPipeline
from ocr.normalizer import OCRNormalizer
from ocr.router import OCREngineRouter
from preprocessing.pipeline import PreprocessingPipeline
from schemas.document import DocumentQuality
from schemas.output import DocumentConfidence, DocumentProcessingOutput
from validation.pipeline import ValidationPipeline


class LandRecordAIPipeline:
    """
    Unified end-to-end processing pipeline orchestrating:
    Document Preprocessing -> Multi-Engine OCR -> Hybrid NLP Extraction ->
    Validation Engine -> Explainable Confidence Scorer -> Canonical Document Output.
    """

    def __init__(
        self,
        config_dir: Optional[str] = None,
        save_debug_artifacts: bool = False,
        debug_output_dir: Optional[str] = None
    ):
        base_cfg = config_dir or os.path.join(os.path.dirname(__file__), "config")
        
        self.preprocessing = PreprocessingPipeline(
            config_path=os.path.join(base_cfg, "thresholds.yaml"),
            save_debug_artifacts=save_debug_artifacts,
            debug_output_dir=debug_output_dir
        )
        self.normalizer = OCRNormalizer(
            languages_config_path=os.path.join(base_cfg, "languages.yaml")
        )
        self.ocr_router = OCREngineRouter(normalizer=self.normalizer)
        self.extraction = ExtractionPipeline(
            fields_config_path=os.path.join(base_cfg, "fields.yaml"),
            state_rules_dir=os.path.join(base_cfg, "state_rules")
        )
        self.validation = ValidationPipeline(
            state_rules_dir=os.path.join(base_cfg, "state_rules")
        )
        self.confidence_scorer = ExplainableConfidenceScorer(
            thresholds_config_path=os.path.join(base_cfg, "thresholds.yaml")
        )

    def process(
        self,
        image: Union[np.ndarray, Image.Image, str],
        document_id: Optional[str] = None,
        preferred_engine: Optional[str] = None,
        language: Optional[str] = None,
        is_handwritten: bool = False,
        page_number: int = 1
    ) -> DocumentProcessingOutput:
        """
        Execute full digitization and explainable AI extraction pipeline on a single page or document.
        """
        start_time = time.perf_counter()
        doc_id = document_id or f"doc_{uuid.uuid4().hex[:8]}"

        # 1. Image Preprocessing & Quality Analysis
        preproc_result = self.preprocessing.process(image)
        quality_analysis = preproc_result.quality_analysis
        enhanced_image = preproc_result.processed_image

        # 2. Multi-Engine OCR with Router & Fallback
        ocr_result, ocr_summary = self.ocr_router.recognize(
            image=enhanced_image if isinstance(enhanced_image, np.ndarray) else image,
            preferred_engine=preferred_engine,
            language=language,
            is_handwritten=is_handwritten,
            quality_score=quality_analysis.laplacian_variance,
            quality_grade=quality_analysis.quality
        )

        # 3. Hybrid NLP Field Extraction
        extracted_fields = self.extraction.extract(ocr_result)

        # 4. Multi-Level Validation
        validation_report = self.validation.validate(extracted_fields)

        # 5. Explainable Confidence Scoring & Review Routing
        doc_confidence, field_confidences, explanations, needs_review = self.confidence_scorer.score_document(
            quality=quality_analysis,
            ocr_summary=ocr_summary,
            fields=extracted_fields,
            validation_report=validation_report
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return DocumentProcessingOutput(
            document_id=doc_id,
            pages=1,
            document_quality=quality_analysis,
            ocr=ocr_summary,
            fields=extracted_fields,
            confidence=doc_confidence,
            explanations=explanations,
            needs_human_review=needs_review,
            field_confidences=field_confidences,
            processing_time_ms=latency_ms
        )
