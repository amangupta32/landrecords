"""Unit tests for document preprocessing and quality analysis modules."""

import pytest
import numpy as np
import cv2
from PIL import Image

from preprocessing.grayscale import GrayscaleConverter
from preprocessing.denoise import NoiseReducer
from preprocessing.clahe import CLAHEEnhancer
from preprocessing.deskew import Deskewer
from preprocessing.threshold import ThresholdProcessor
from preprocessing.quality import QualityAnalyzer
from preprocessing.pipeline import PreprocessingPipeline
from schemas.document import PreprocessingResult, DocumentQuality


@pytest.fixture
def sample_bgr_image() -> np.ndarray:
    """Create a synthetic 3-channel BGR document image with text-like strokes."""
    img = np.full((300, 400, 3), 240, dtype=np.uint8)
    # Add dark text-like horizontal lines
    cv2.putText(img, "UTTARAKHAND LAND RECORD - KHASRA 123", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20, 20, 20), 2)
    cv2.putText(img, "OWNER: RAMESH SINGH S/O MOHAN SINGH", (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20, 20, 20), 2)
    cv2.putText(img, "AREA: 2.5000 HECTARE, VILLAGE: RAJPUR", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20, 20, 20), 2)
    return img


@pytest.fixture
def sample_pil_image(sample_bgr_image) -> Image.Image:
    """Create a PIL RGB Image."""
    rgb = cv2.cvtColor(sample_bgr_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


class TestGrayscaleConverter:
    """Test GrayscaleConverter handles various inputs accurately."""

    def test_bgr_to_grayscale(self, sample_bgr_image):
        gray = GrayscaleConverter.convert(sample_bgr_image)
        assert isinstance(gray, np.ndarray)
        assert gray.ndim == 2
        assert gray.shape == (300, 400)
        assert gray.dtype == np.uint8

    def test_pil_image_conversion(self, sample_pil_image):
        gray = GrayscaleConverter.convert(sample_pil_image)
        assert gray.ndim == 2
        assert gray.shape == (300, 400)
        assert gray.dtype == np.uint8

    def test_rgba_conversion(self):
        rgba = np.full((100, 100, 4), 200, dtype=np.uint8)
        gray = GrayscaleConverter.convert(rgba)
        assert gray.shape == (100, 100)
        assert gray.ndim == 2

    def test_already_grayscale_image(self):
        gray_input = np.full((150, 150), 128, dtype=np.uint8)
        result = GrayscaleConverter.convert(gray_input)
        assert result.shape == (150, 150)
        assert np.array_equal(result, gray_input)

    def test_empty_image_raises_error(self):
        empty_img = np.array([])
        with pytest.raises(ValueError):
            GrayscaleConverter.convert(empty_img)

    def test_invalid_type_raises_error(self):
        with pytest.raises(TypeError):
            GrayscaleConverter.convert("invalid_string_input")  # type: ignore


class TestNoiseReducer:
    """Test edge-preserving noise reduction methods."""

    def test_nlmeans_denoising(self, sample_bgr_image):
        reducer = NoiseReducer(method="nlmeans", h=10.0)
        denoised = reducer.denoise(sample_bgr_image)
        assert denoised.shape == (300, 400)
        assert denoised.dtype == np.uint8

    def test_bilateral_denoising(self, sample_bgr_image):
        reducer = NoiseReducer(method="bilateral")
        denoised = reducer.denoise(sample_bgr_image)
        assert denoised.shape == (300, 400)
        assert denoised.dtype == np.uint8


class TestCLAHEEnhancer:
    """Test CLAHE local contrast enhancement."""

    def test_clahe_enhancement(self, sample_bgr_image):
        enhancer = CLAHEEnhancer(clip_limit=2.0, tile_grid_size=(8, 8))
        enhanced = enhancer.enhance(sample_bgr_image)
        assert enhanced.shape == (300, 400)
        assert enhanced.dtype == np.uint8
        # Standard deviation of enhanced image should be non-zero
        assert np.std(enhanced) > 0


class TestDeskewer:
    """Test Hough transform skew estimation and rotation safeguards."""

    def test_deskew_straight_image(self, sample_bgr_image):
        deskewer = Deskewer(min_confidence=0.35)
        deskewed, meta = deskewer.deskew(sample_bgr_image)
        assert deskewed.shape == (300, 400)
        # Straight image should have near zero rotation angle
        assert abs(meta.rotation_angle) < 5.0

    def test_deskew_rotated_synthetic_lines(self):
        # Create an image with distinct rotated parallel horizontal lines
        h, w = 600, 800
        canvas = np.full((h, w), 255, dtype=np.uint8)
        for y in range(80, 520, 40):
            cv2.line(canvas, (50, y), (750, y), 0, 3)

        # Rotate by 4.0 degrees
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, 4.0, 1.0)
        rotated = cv2.warpAffine(canvas, rot_mat, (w, h), borderValue=255)

        deskewer = Deskewer(max_angle=45.0, min_confidence=0.20, hough_threshold=50, min_line_length=50)
        deskewed, meta = deskewer.deskew(rotated)

        assert deskewed.shape == (h, w)
        assert meta.was_rotated is True
        # Detected skew angle magnitude should match applied 4.0 degrees
        assert abs(abs(meta.rotation_angle) - 4.0) < 1.5


class TestThresholdProcessor:
    """Test Otsu binarization produces clean binary outputs."""

    def test_otsu_thresholding(self, sample_bgr_image):
        processor = ThresholdProcessor(method="otsu")
        binary = processor.binarize(sample_bgr_image)
        assert binary.shape == (300, 400)
        # Unique pixel values should only be 0 (black) and 255 (white)
        unique_vals = set(np.unique(binary))
        assert unique_vals.issubset({0, 255})


class TestQualityAnalyzer:
    """Test Laplacian blur variance scoring and quality classification."""

    def test_sharp_image_quality(self, sample_bgr_image):
        analyzer = QualityAnalyzer(blur_threshold=50.0, acceptable_threshold=150.0)
        quality = analyzer.analyze(sample_bgr_image)

        assert isinstance(quality, DocumentQuality)
        assert quality.laplacian_variance > 50.0
        assert quality.quality in ("acceptable", "good")
        assert quality.is_blurry is False
        assert quality.width == 400
        assert quality.height == 300

    def test_blurry_image_quality(self, sample_bgr_image):
        # Heavily blur the image
        blurry = cv2.GaussianBlur(sample_bgr_image, (35, 35), 15.0)
        analyzer = QualityAnalyzer(blur_threshold=100.0, acceptable_threshold=250.0)
        quality = analyzer.analyze(blurry)

        assert quality.laplacian_variance < 100.0
        assert quality.quality == "poor"
        assert quality.is_blurry is True


class TestPreprocessingPipeline:
    """Test end-to-end PreprocessingPipeline execution and typed results."""

    def test_pipeline_process(self, sample_bgr_image):
        pipeline = PreprocessingPipeline(save_debug_artifacts=False)
        result = pipeline.process(sample_bgr_image)

        assert isinstance(result, PreprocessingResult)
        assert isinstance(result.processed_image, np.ndarray)
        assert result.processed_image.shape == (300, 400)
        assert result.quality in ("good", "acceptable", "poor")
        assert result.blur_score > 0.0
        assert result.deskew_details is not None
        assert result.metadata.processing_steps == [
            "quality_analysis",
            "grayscale",
            "denoise",
            "clahe",
            "deskew",
            "otsu",
        ]
        assert result.variants is not None
        assert "original" in result.variants
        assert "grayscale" in result.variants
        assert "denoised" in result.variants
        assert "clahe" in result.variants
        assert "deskewed" in result.variants
        assert "otsu" in result.variants

    def test_pipeline_debug_artifacts(self, sample_bgr_image, tmp_path):
        pipeline = PreprocessingPipeline(save_debug_artifacts=True, debug_output_dir=tmp_path)
        result = pipeline.process(sample_bgr_image, save_debug=True, debug_dir=tmp_path)

        assert (tmp_path / "01_original.png").exists()
        assert (tmp_path / "02_grayscale.png").exists()
        assert (tmp_path / "03_denoised.png").exists()
        assert (tmp_path / "04_clahe.png").exists()
        assert (tmp_path / "05_deskewed.png").exists()
        assert (tmp_path / "06_otsu.png").exists()
        assert result.metadata.original_shape == [300, 400, 3]
        assert result.metadata.final_shape == [300, 400]

    def test_individual_stages_callable(self, sample_bgr_image):
        pipeline = PreprocessingPipeline()
        gray = pipeline.to_grayscale(sample_bgr_image)
        assert gray.ndim == 2

        denoised = pipeline.denoise(gray)
        assert denoised.shape == gray.shape

        clahe = pipeline.apply_clahe(denoised)
        assert clahe.shape == gray.shape

        deskewed, meta = pipeline.deskew(clahe)
        assert deskewed.shape == gray.shape

        otsu = pipeline.apply_otsu(deskewed)
        assert otsu.shape == gray.shape

        quality = pipeline.analyze_quality(sample_bgr_image)
        assert quality.width == 400
