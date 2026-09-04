"""Binarization and thresholding module for document preprocessing."""

from typing import Optional, Tuple
import cv2
import numpy as np

from preprocessing.grayscale import GrayscaleConverter


class ThresholdProcessor:
    """Performs global Otsu and local adaptive binarization on document images."""

    def __init__(
        self,
        method: str = "otsu",
        block_size: int = 11,
        c_constant: int = 2,
    ):
        """
        Initialize ThresholdProcessor.

        Args:
            method: Binarization method: 'otsu', 'adaptive_gaussian', 'adaptive_mean'.
            block_size: Size of a pixel neighborhood for adaptive thresholding (odd int).
            c_constant: Constant subtracted from the mean or weighted mean in adaptive.
        """
        self.method = method.lower()
        self.block_size = block_size if block_size % 2 == 1 else block_size + 1
        self.c_constant = c_constant

    def binarize(self, image: np.ndarray) -> np.ndarray:
        """
        Binarize grayscale image to high-contrast black & white (0 and 255).

        Args:
            image: Single-channel 8-bit grayscale image.

        Returns:
            np.ndarray: Binarized uint8 image (255 background, 0 text, or standard binary).
        """
        gray = GrayscaleConverter.convert(image)

        if self.method == "otsu":
            # Global Otsu's thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary
        elif self.method == "adaptive_gaussian":
            return cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self.block_size,
                self.c_constant
            )
        elif self.method == "adaptive_mean":
            return cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                self.block_size,
                self.c_constant
            )
        else:
            # Default to Otsu
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary

    @staticmethod
    def apply_otsu(image: np.ndarray) -> np.ndarray:
        """Direct helper to apply Otsu thresholding."""
        gray = GrayscaleConverter.convert(image)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
