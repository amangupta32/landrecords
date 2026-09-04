"""Document Quality Analysis module: Laplacian blur scoring, contrast, brightness, and resolution."""

from typing import Optional, Union, Dict, Any
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import yaml

from preprocessing.grayscale import GrayscaleConverter
from schemas.document import DocumentQuality


class QualityAnalyzer:
    """Computes Laplacian blur score, contrast, brightness, and resolution metrics for land record documents."""

    def __init__(
        self,
        blur_threshold: float = 100.0,
        acceptable_threshold: float = 250.0,
        min_width: int = 600,
        min_height: int = 600,
        min_resolution_dpi: int = 150,
        config_path: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize QualityAnalyzer.

        Args:
            blur_threshold: Laplacian variance below which image is considered blurry/poor.
            acceptable_threshold: Laplacian variance above which image is considered good.
            min_width: Minimum acceptable image width.
            min_height: Minimum acceptable image height.
            min_resolution_dpi: Minimum recommended DPI.
            config_path: Optional path to thresholds.yaml.
        """
        self.blur_threshold = float(blur_threshold)
        self.acceptable_threshold = float(acceptable_threshold)
        self.min_width = int(min_width)
        self.min_height = int(min_height)
        self.min_resolution_dpi = int(min_resolution_dpi)

        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path: Union[str, Path]) -> None:
        """Load quality thresholds from YAML configuration."""
        try:
            path = Path(config_path)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if cfg and "quality" in cfg:
                        q = cfg["quality"]
                        self.blur_threshold = float(q.get("blur_threshold", self.blur_threshold))
                        self.acceptable_threshold = float(q.get("acceptable_threshold", self.acceptable_threshold))
                        self.min_width = int(q.get("min_width", self.min_width))
                        self.min_height = int(q.get("min_height", self.min_height))
                        self.min_resolution_dpi = int(q.get("min_resolution_dpi", self.min_resolution_dpi))
        except Exception as err:
            # Fall back to default initialized values
            pass

    def compute_laplacian_variance(self, image: np.ndarray) -> float:
        """
        Compute the variance of Laplacian operator over the grayscale image.

        variance of Laplacian(image) = Var(cv2.Laplacian(image, cv2.CV_64F))

        Returns:
            float: Variance score (higher means sharper edges).
        """
        gray = GrayscaleConverter.convert(image)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = float(laplacian.var())
        return round(variance, 2)

    def analyze(
        self,
        image: Union[np.ndarray, Image.Image],
        dpi: Optional[int] = None
    ) -> DocumentQuality:
        """
        Perform comprehensive document quality analysis.

        Args:
            image: Input image (numpy array or PIL Image).
            dpi: Optional known or extracted DPI.

        Returns:
            DocumentQuality: Typed Pydantic quality result.
        """
        # If PIL Image, attempt to read DPI metadata if not provided
        if isinstance(image, Image.Image) and dpi is None:
            info = image.info
            if "dpi" in info:
                dpi_val = info["dpi"]
                if isinstance(dpi_val, (tuple, list)):
                    dpi = int(dpi_val[0])
                elif isinstance(dpi_val, (int, float)):
                    dpi = int(dpi_val)

        gray = GrayscaleConverter.convert(image)
        h, w = gray.shape[:2]

        laplacian_var = self.compute_laplacian_variance(gray)
        brightness = float(round(float(np.mean(gray)), 2))
        contrast = float(round(float(np.std(gray)), 2))

        # Classify blur and overall quality
        is_blurry = laplacian_var < self.blur_threshold

        if laplacian_var >= self.acceptable_threshold:
            quality_grade = "good"
        elif laplacian_var >= self.blur_threshold:
            quality_grade = "acceptable"
        else:
            quality_grade = "poor"

        # Check resolution degradation
        if w < self.min_width or h < self.min_height:
            if quality_grade == "good":
                quality_grade = "acceptable"

        return DocumentQuality(
            laplacian_variance=laplacian_var,
            quality=quality_grade,
            brightness=brightness,
            contrast=contrast,
            width=w,
            height=h,
            dpi=dpi,
            is_blurry=is_blurry
        )
