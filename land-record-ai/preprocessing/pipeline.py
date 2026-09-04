"""Orchestrator for the OpenCV document preprocessing pipeline."""

import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
import cv2
import numpy as np
from PIL import Image
import yaml

from preprocessing.grayscale import GrayscaleConverter
from preprocessing.denoise import NoiseReducer
from preprocessing.clahe import CLAHEEnhancer
from preprocessing.deskew import Deskewer
from preprocessing.threshold import ThresholdProcessor
from preprocessing.quality import QualityAnalyzer
from schemas.document import (
    DocumentQuality,
    DeskewMetadata,
    PreprocessingMetadata,
    PreprocessingResult,
)


class PreprocessingPipeline:
    """Production-grade modular OpenCV document preprocessing pipeline for Indian land records."""

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        save_debug_artifacts: bool = False,
        debug_output_dir: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize the preprocessing pipeline with all sub-modules.

        Args:
            config_path: Optional path to thresholds.yaml.
            save_debug_artifacts: If True, saves intermediate images to disk.
            debug_output_dir: Directory where debug images will be stored.
        """
        self.config_path = Path(config_path) if config_path else self._find_default_config()
        self.save_debug_artifacts = save_debug_artifacts
        self.debug_output_dir = Path(debug_output_dir) if debug_output_dir else Path("./data/processed/debug")

        # Load configurations
        config = self._load_yaml_config(self.config_path)

        # Initialize sub-modules with externalized config
        q_cfg = config.get("quality", {})
        self.quality_analyzer = QualityAnalyzer(
            blur_threshold=q_cfg.get("blur_threshold", 100.0),
            acceptable_threshold=q_cfg.get("acceptable_threshold", 250.0),
            min_width=q_cfg.get("min_width", 600),
            min_height=q_cfg.get("min_height", 600),
            min_resolution_dpi=q_cfg.get("min_resolution_dpi", 150),
        )

        prep_cfg = config.get("preprocessing", {})
        clahe_cfg = prep_cfg.get("clahe", {})
        self.clahe_enhancer = CLAHEEnhancer(
            clip_limit=clahe_cfg.get("clip_limit", 2.0),
            tile_grid_size=clahe_cfg.get("tile_grid_size", [8, 8]),
        )

        denoise_cfg = prep_cfg.get("denoise", {})
        self.noise_reducer = NoiseReducer(
            method=denoise_cfg.get("method", "nlmeans"),
            h=denoise_cfg.get("h", 10.0),
            template_window_size=denoise_cfg.get("template_window_size", 7),
            search_window_size=denoise_cfg.get("search_window_size", 21),
        )

        deskew_cfg = prep_cfg.get("deskew", {})
        self.deskewer = Deskewer(
            max_angle=deskew_cfg.get("max_angle", 45.0),
            min_confidence=deskew_cfg.get("min_confidence", 0.35),
            hough_threshold=deskew_cfg.get("hough_threshold", 100),
            min_line_length=deskew_cfg.get("min_line_length", 100),
            max_line_gap=deskew_cfg.get("max_line_gap", 10),
            angle_resolution_deg=deskew_cfg.get("angle_resolution_deg", 0.5),
        )

        thresh_cfg = prep_cfg.get("threshold", {})
        self.threshold_processor = ThresholdProcessor(
            method=thresh_cfg.get("method", "otsu"),
            block_size=thresh_cfg.get("block_size", 11),
            c_constant=thresh_cfg.get("c_constant", 2),
        )

    def _find_default_config(self) -> Optional[Path]:
        """Attempt to resolve default config path."""
        candidates = [
            Path(__file__).resolve().parent.parent / "config" / "thresholds.yaml",
            Path("./config/thresholds.yaml"),
            Path("../config/thresholds.yaml"),
        ]
        for p in candidates:
            if p.exists():
                return p
        return None

    def _load_yaml_config(self, path: Optional[Path]) -> Dict[str, Any]:
        """Safely load YAML config file."""
        if path and path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                return {}
        return {}

    # --- Independent Callable Stage Helpers ---

    def to_grayscale(self, image: Union[np.ndarray, Image.Image]) -> np.ndarray:
        """Independently convert input image to grayscale."""
        return GrayscaleConverter.convert(image)

    def denoise(self, image: np.ndarray) -> np.ndarray:
        """Independently denoise image."""
        return self.noise_reducer.denoise(image)

    def apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """Independently apply CLAHE contrast enhancement."""
        return self.clahe_enhancer.enhance(image)

    def deskew(self, image: np.ndarray) -> tuple[np.ndarray, DeskewMetadata]:
        """Independently deskew image."""
        return self.deskewer.deskew(image)

    def apply_otsu(self, image: np.ndarray) -> np.ndarray:
        """Independently apply Otsu thresholding."""
        return self.threshold_processor.binarize(image)

    def analyze_quality(self, image: Union[np.ndarray, Image.Image], dpi: Optional[int] = None) -> DocumentQuality:
        """Independently analyze document quality and blur score."""
        return self.quality_analyzer.analyze(image, dpi=dpi)

    # --- Full Sequential Preprocessing Execution ---

    def process(
        self,
        image: Union[np.ndarray, Image.Image, str, Path],
        dpi: Optional[int] = None,
        save_debug: Optional[bool] = None,
        debug_dir: Optional[Union[str, Path]] = None,
    ) -> PreprocessingResult:
        """
        Execute full standard preprocessing pipeline:
        Original -> Quality Analysis -> Grayscale -> Denoising -> CLAHE -> Deskew -> Otsu.

        Args:
            image: Input image (numpy array, PIL Image, or file path).
            dpi: Optional known DPI.
            save_debug: Override debug saving flag.
            debug_dir: Override debug output directory.

        Returns:
            PreprocessingResult: Typed Pydantic object containing processed image,
                                 blur score, quality tier, rotation angle,
                                 deskew confidence, metadata, and all variants.
        """
        start_time = time.perf_counter()
        steps_executed = []

        # 1. Load image
        if isinstance(image, (str, Path)):
            img_path = Path(image)
            if not img_path.exists():
                raise FileNotFoundError(f"Image file not found: {img_path}")
            raw_img = cv2.imread(str(img_path))
            if raw_img is None:
                raise ValueError(f"Failed to decode image from path: {img_path}")
        elif isinstance(image, Image.Image):
            raw_img = np.array(image)
        elif isinstance(image, np.ndarray):
            raw_img = image.copy()
        else:
            raise TypeError(f"Unsupported image input type: {type(image)}")

        orig_shape = list(raw_img.shape)

        # 2. Document Quality Analysis (Laplacian Blur, Brightness, Contrast, DPI)
        quality_analysis = self.quality_analyzer.analyze(raw_img, dpi=dpi)
        steps_executed.append("quality_analysis")

        # 3. Grayscale Conversion
        gray_img = self.to_grayscale(raw_img)
        steps_executed.append("grayscale")

        # 4. Noise Reduction (Edge-preserving Fast Non-Local Means / Bilateral)
        denoised_img = self.denoise(gray_img)
        steps_executed.append("denoise")

        # 5. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe_img = self.apply_clahe(denoised_img)
        steps_executed.append("clahe")

        # 6. Hough Transform Deskewing
        deskewed_img, deskew_details = self.deskew(clahe_img)
        steps_executed.append("deskew")

        # 7. Otsu Binarization (OCR-Ready Binary Image)
        otsu_img = self.apply_otsu(deskewed_img)
        steps_executed.append("otsu")

        # Collect all preprocessing variants for the OCR router
        variants = {
            "original": raw_img,
            "grayscale": gray_img,
            "denoised": denoised_img,
            "clahe": clahe_img,
            "deskewed": deskewed_img,
            "otsu": otsu_img,
        }

        # Optional debug artifacts saving for traceability
        should_save_debug = self.save_debug_artifacts if save_debug is None else save_debug
        if should_save_debug:
            out_dir = Path(debug_dir) if debug_dir else self.debug_output_dir
            out_dir.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(out_dir / "01_original.png"), raw_img if raw_img.ndim == 2 or raw_img.shape[2] == 3 else cv2.cvtColor(raw_img, cv2.COLOR_RGBA2BGR))
            cv2.imwrite(str(out_dir / "02_grayscale.png"), gray_img)
            cv2.imwrite(str(out_dir / "03_denoised.png"), denoised_img)
            cv2.imwrite(str(out_dir / "04_clahe.png"), clahe_img)
            cv2.imwrite(str(out_dir / "05_deskewed.png"), deskewed_img)
            cv2.imwrite(str(out_dir / "06_otsu.png"), otsu_img)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        metadata = PreprocessingMetadata(
            processing_steps=steps_executed,
            rotation_angle=deskew_details.rotation_angle,
            deskew_confidence=deskew_details.deskew_confidence,
            blur_score=quality_analysis.laplacian_variance,
            quality=quality_analysis.quality,
            original_shape=orig_shape,
            final_shape=list(otsu_img.shape),
            duration_ms=round(duration_ms, 2),
        )

        return PreprocessingResult(
            processed_image=otsu_img,
            blur_score=quality_analysis.laplacian_variance,
            quality=quality_analysis.quality,
            rotation_angle=deskew_details.rotation_angle,
            deskew_confidence=deskew_details.deskew_confidence,
            quality_analysis=quality_analysis,
            deskew_details=deskew_details,
            metadata=metadata,
            variants=variants,
        )
