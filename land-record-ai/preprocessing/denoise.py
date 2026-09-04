"""Noise reduction module for document preprocessing."""

from typing import Optional
import cv2
import numpy as np

from preprocessing.grayscale import GrayscaleConverter


class NoiseReducer:
    """Removes noise artifacts, paper speckles, and scanner grain while preserving text stroke edges."""

    def __init__(
        self,
        method: str = "nlmeans",
        h: float = 10.0,
        template_window_size: int = 7,
        search_window_size: int = 21,
        bilateral_d: int = 9,
        bilateral_sigma_color: float = 75.0,
        bilateral_sigma_space: float = 75.0,
    ):
        """
        Initialize NoiseReducer with filter parameters.

        Args:
            method: Denoising technique ('nlmeans', 'bilateral', 'gaussian', 'median').
            h: Filter strength for fastNlMeans.
            template_window_size: Size in pixels of template patch for fastNlMeans (odd integer).
            search_window_size: Size in pixels of search window for fastNlMeans (odd integer).
            bilateral_d: Diameter of each pixel neighborhood for bilateral filter.
            bilateral_sigma_color: Filter sigma in color space for bilateral filter.
            bilateral_sigma_space: Filter sigma in coordinate space for bilateral filter.
        """
        self.method = method.lower()
        self.h = float(h)
        self.template_window_size = int(template_window_size)
        self.search_window_size = int(search_window_size)
        self.bilateral_d = int(bilateral_d)
        self.bilateral_sigma_color = float(bilateral_sigma_color)
        self.bilateral_sigma_space = float(bilateral_sigma_space)

    def denoise(self, image: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction filter on grayscale image.

        Args:
            image: Single-channel 8-bit grayscale image (or multi-channel converted automatically).

        Returns:
            np.ndarray: Denoised 8-bit grayscale image.
        """
        gray = GrayscaleConverter.convert(image)

        if self.method == "nlmeans":
            # Fast Non-Local Means Denoising
            # Ensure odd window sizes
            t_size = self.template_window_size if self.template_window_size % 2 == 1 else self.template_window_size + 1
            s_size = self.search_window_size if self.search_window_size % 2 == 1 else self.search_window_size + 1
            return cv2.fastNlMeansDenoising(
                gray,
                None,
                h=self.h,
                templateWindowSize=t_size,
                searchWindowSize=s_size
            )
        elif self.method == "bilateral":
            # Edge-preserving Bilateral Filter
            return cv2.bilateralFilter(
                gray,
                d=self.bilateral_d,
                sigmaColor=self.bilateral_sigma_color,
                sigmaSpace=self.bilateral_sigma_space
            )
        elif self.method == "gaussian":
            return cv2.GaussianBlur(gray, (5, 5), 0)
        elif self.method == "median":
            return cv2.medianBlur(gray, 3)
        else:
            # Fallback to nlmeans
            return cv2.fastNlMeansDenoising(gray, None, h=self.h, templateWindowSize=7, searchWindowSize=21)
