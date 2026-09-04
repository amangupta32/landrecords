"""Contrast Limited Adaptive Histogram Equalization (CLAHE) module."""

from typing import Tuple, Union
import cv2
import numpy as np

from preprocessing.grayscale import GrayscaleConverter


class CLAHEEnhancer:
    """Enhances local contrast in document images using Contrast Limited Adaptive Histogram Equalization."""

    def __init__(self, clip_limit: float = 2.0, tile_grid_size: Union[Tuple[int, int], list] = (8, 8)):
        """
        Initialize CLAHE enhancer.

        Args:
            clip_limit: Threshold for contrast limiting (higher increases contrast).
            tile_grid_size: Grid size for local histogram equalization (e.g. (8, 8)).
        """
        self.clip_limit = float(clip_limit)
        grid_tuple = tuple(tile_grid_size) if isinstance(tile_grid_size, (list, tuple)) else (8, 8)
        self.tile_grid_size = (int(grid_tuple[0]), int(grid_tuple[1]))
        self._clahe = cv2.createCLAHE(
            clipLimit=self.clip_limit,
            tileGridSize=self.tile_grid_size
        )

    def enhance(self, image: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE contrast enhancement on grayscale image.

        Args:
            image: Single-channel 8-bit grayscale image.

        Returns:
            np.ndarray: Contrast-enhanced 8-bit grayscale image.
        """
        gray = GrayscaleConverter.convert(image)
        return self._clahe.apply(gray)
