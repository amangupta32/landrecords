"""Unit tests for OCR engines, normalizer, bounding boxes, router, and ensemble."""

import os
import numpy as np
import pytest
from PIL import Image

from ocr.base import OCREngine
from ocr.ensemble import OCREnsemble
from ocr.fallback import LandRecordFallbackEngine
from ocr.indic_htr import IndicHTREngine
from ocr.normalizer import OCRNormalizer
from ocr.paddleocr_engine import PaddleOCREngine
from ocr.router import OCREngineRouter
from ocr.tesseract import TesseractEngine
from schemas.ocr import BoundingBox, OCREngineResult, OCRWord


class TestOCRNormalizer:
    @pytest.fixture
    def normalizer(self):
        return OCRNormalizer()

    def test_devanagari_numeral_translation(self, normalizer):
        raw = "खसरा संख्या २४५/१ एवं खाता संख्या ८९"
        normalized = normalizer.normalize_text(raw)
        assert "245/1" in normalized
        assert "89" in normalized

    def test_devanagari_punctuation(self, normalizer):
        raw = "ग्राम रामपुर। तहसील रामपुर॥"
        normalized = normalizer.normalize_text(raw)
        assert "." in normalized
        assert "।" not in normalized
        assert "॥" not in normalized

    def test_bounding_box_normalization_standard(self, normalizer):
        bbox = [100, 50, 200, 150]
        norm = normalizer.normalize_bbox(bbox, img_width=800, img_height=600)
        assert norm == [100, 50, 200, 150]

    def test_bounding_box_normalization_xywh(self, normalizer):
        xywh = [100, 50, 100, 100]  # x, y, w, h
        norm = normalizer.normalize_bbox(xywh, is_xywh=True)
        assert norm == [100, 50, 200, 150]

    def test_bounding_box_clamping(self, normalizer):
        bbox = [-10, -5, 900, 700]
        norm = normalizer.normalize_bbox(bbox, img_width=800, img_height=600)
        assert norm == [0, 0, 800, 600]

    def test_polygon_to_rect(self, normalizer):
        poly = [[10, 20], [100, 20], [100, 60], [10, 60]]
        rect = normalizer.normalize_polygon_points(poly)
        assert rect == [10, 20, 100, 60]


class TestOCREngines:
    @pytest.fixture
    def synthetic_image(self):
        # 400x300 white RGB image
        return np.full((300, 400, 3), 255, dtype=np.uint8)

    def test_fallback_engine_jamabandi(self, synthetic_image):
        engine = LandRecordFallbackEngine()
        assert engine.is_available() is True
        result = engine.recognize(synthetic_image, template_name="jamabandi")
        assert isinstance(result, OCREngineResult)
        assert result.engine == "fallback"
        assert len(result.words) > 0
        assert len(result.lines) > 0
        assert "245/1" in result.normalized_text
        assert "89" in result.normalized_text
        assert result.average_confidence >= 0.80

    def test_fallback_engine_mutation(self, synthetic_image):
        engine = LandRecordFallbackEngine()
        result = engine.recognize(synthetic_image, template_name="mutation")
        assert "118" in result.normalized_text
        assert "42" in result.normalized_text
        assert "MUT-2022-104" in result.normalized_text

    def test_fallback_engine_saledeed(self, synthetic_image):
        engine = LandRecordFallbackEngine()
        result = engine.recognize(synthetic_image, template_name="saledeed")
        assert "SALE DEED" in result.text
        assert "245/1" in result.normalized_text

    def test_indic_htr_engine(self, synthetic_image):
        engine = IndicHTREngine()
        assert engine.is_available() is True
        result = engine.recognize(synthetic_image)
        assert result.engine == "indic_htr"
        assert len(result.words) > 0
        assert result.metadata.get("handwritten_mode") is True

    def test_tesseract_availability_check(self):
        engine = TesseractEngine()
        assert isinstance(engine.is_available(), bool)

    def test_paddleocr_availability_check(self):
        engine = PaddleOCREngine()
        assert isinstance(engine.is_available(), bool)


class TestOCREngineRouter:
    def test_router_selection_and_recognition(self):
        router = OCREngineRouter()
        available = router.get_available_engines()
        assert "fallback" in available
        assert "indic_htr" in available

        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        result, summary = router.recognize(img)
        assert isinstance(result, OCREngineResult)
        assert summary.primary_engine in available
        assert len(summary.engines_executed) >= 1

    def test_router_handwritten_preference(self):
        router = OCREngineRouter()
        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        result, summary = router.recognize(img, is_handwritten=True)
        assert result.engine == "indic_htr"


class TestOCREnsemble:
    def test_ensemble_single_result(self):
        engine = LandRecordFallbackEngine()
        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        res = engine.recognize(img)
        
        ensemble = OCREnsemble()
        ens_res, summary = ensemble.ensemble_results([res])
        assert ens_res.engine == res.engine
        assert summary.agreement_score == 1.0

    def test_ensemble_multi_results(self):
        engine_fallback = LandRecordFallbackEngine()
        img = np.full((300, 400, 3), 255, dtype=np.uint8)
        res1 = engine_fallback.recognize(img, template_name="jamabandi")
        res2 = engine_fallback.recognize(img, template_name="jamabandi")

        ensemble = OCREnsemble()
        ens_res, summary = ensemble.ensemble_results([res1, res2])
        assert ens_res.engine == "ensemble"
        assert summary.agreement_score == 1.0
        assert ens_res.average_confidence >= 0.8
