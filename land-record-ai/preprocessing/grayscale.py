"""Grayscale conversion module for document preprocessing."""

from typing import Union
import cv2
import numpy as np
from PIL import Image


class GrayscaleConverter:
    """Converts multi-channel document images into standardized 8-bit single-channel grayscale."""

    @staticmethod
    def convert(image: Union[np.ndarray, Image.Image]) -> np.ndarray:
        """
        Convert an input image to single-channel 8-bit grayscale.

        Args:
            image: Input image as numpy ndarray or PIL Image.

        Returns:
            np.ndarray: 2D uint8 numpy array representing grayscale image.

        Raises:
            ValueError: If input image is empty or invalid shape.
        """
        if isinstance(image, Image.Image):
            # Convert PIL Image to RGB numpy array first if needed
            if image.mode == "L":
                return np.array(image, dtype=np.uint8)
            image_np = np.array(image)
            if image.mode in ("RGBA", "LA") or (image_np.ndim == 3 and image_np.shape[2] == 4):
                return cv2.cvtColor(image_np, cv2.COLOR_RGBA2GRAY)
            return cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        if not isinstance(image, np.ndarray):
            raise TypeError(f"Expected np.ndarray or PIL.Image, got {type(image)}")

        if image.size == 0:
            raise ValueError("Input image array is empty (size 0)")

        # Handle floating point images
        if np.issubdtype(image.dtype, np.floating):
            if image.max() <= 1.0:
                image = (image * 255.0).astype(np.uint8)
            else:
                image = np.clip(image, 0, 255).astype(np.uint8)
        elif image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)

        # Check dimensions
        if image.ndim == 2:
            return image.copy()
        elif image.ndim == 3:
            channels = image.shape[2]
            if channels == 1:
                return image[:, :, 0].copy()
            elif channels == 3:
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            elif channels == 4:
                return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
            else:
                raise ValueError(f"Unsupported number of image channels: {channels}")
        else:
            raise ValueError(f"Unsupported image array dimensions: {image.ndim}")
