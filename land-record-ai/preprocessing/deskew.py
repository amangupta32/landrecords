"""Hough Transform based document deskewing module with confidence safeguards."""

import math
from typing import Tuple
import cv2
import numpy as np

from preprocessing.grayscale import GrayscaleConverter
from schemas.document import DeskewMetadata


class Deskewer:
    """Detects and corrects document skew using Probabilistic Hough Transform and contour analysis."""

    def __init__(
        self,
        max_angle: float = 45.0,
        min_confidence: float = 0.35,
        hough_threshold: int = 100,
        min_line_length: int = 100,
        max_line_gap: int = 10,
        angle_resolution_deg: float = 0.5,
    ):
        """
        Initialize Deskewer.

        Args:
            max_angle: Maximum allowable rotation angle in degrees (above this, skip rotation).
            min_confidence: Minimum line-consensus confidence required to trigger rotation.
            hough_threshold: Accumulator threshold parameter for HoughLinesP.
            min_line_length: Minimum line length in pixels to consider for deskew.
            max_line_gap: Maximum allowed gap between points on the same line to link them.
            angle_resolution_deg: Angle resolution bin size.
        """
        self.max_angle = float(max_angle)
        self.min_confidence = float(min_confidence)
        self.hough_threshold = int(hough_threshold)
        self.min_line_length = int(min_line_length)
        self.max_line_gap = int(max_line_gap)
        self.angle_resolution_deg = float(angle_resolution_deg)

    def estimate_skew(self, image: np.ndarray) -> Tuple[float, float, str]:
        """
        Estimate skew angle and confidence from an image.

        Returns:
            Tuple[float, float, str]: (angle_in_degrees, confidence, method_used)
        """
        gray = GrayscaleConverter.convert(image)
        h, w = gray.shape[:2]

        # Dynamic parameter scaling for small/large images
        min_len = max(20, min(self.min_line_length, int(min(h, w) * 0.15)))
        threshold = max(30, min(self.hough_threshold, int(min_len * 0.8)))

        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Morphological dilation to connect text line strokes into horizontal blocks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
        dilated_edges = cv2.dilate(edges, kernel, iterations=1)

        lines = cv2.HoughLinesP(
            dilated_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=threshold,
            minLineLength=min_len,
            maxLineGap=self.max_line_gap
        )

        angles = []
        weights = []

        if lines is not None and len(lines) > 0:
            lines = lines.reshape(-1, 4)
            for x1, y1, x2, y2 in lines:
                dx = float(x2 - x1)
                dy = float(y2 - y1)
                length = math.hypot(dx, dy)
                if length < min_len:
                    continue

                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)

                # Normalize angle to [-90, 90]
                if angle_deg > 45:
                    angle_deg -= 90
                elif angle_deg < -45:
                    angle_deg += 90

                # Only consider near-horizontal document text lines
                if abs(angle_deg) <= self.max_angle:
                    angles.append(angle_deg)
                    weights.append(length)

        if len(angles) >= 3 and sum(weights) > 0:
            angles_np = np.array(angles)
            weights_np = np.array(weights)

            # Weighted median estimation
            sort_indices = np.argsort(angles_np)
            sorted_angles = angles_np[sort_indices]
            sorted_weights = weights_np[sort_indices]
            cumsum = np.cumsum(sorted_weights)
            cutoff = cumsum[-1] / 2.0
            median_idx = np.searchsorted(cumsum, cutoff)
            dominant_angle = float(sorted_angles[min(median_idx, len(sorted_angles) - 1)])

            # Confidence is the proportion of line weight within ±2 degrees of dominant angle
            aligned_weight = np.sum(weights_np[np.abs(angles_np - dominant_angle) <= 2.0])
            total_weight = np.sum(weights_np)
            confidence = float(min(1.0, (aligned_weight / total_weight) * min(1.0, len(angles) / 10.0)))

            return dominant_angle, confidence, "hough_lines"

        # Fallback: Contour bounding box orientation analysis
        # Threshold to extract text blobs
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) > 500:
            min_rect = cv2.minAreaRect(coords)
            angle = min_rect[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            if abs(angle) <= self.max_angle:
                return float(angle), 0.40, "contour_min_area"

        return 0.0, 0.0, "none"

    def deskew(self, image: np.ndarray) -> Tuple[np.ndarray, DeskewMetadata]:
        """
        Deskew an image if confident skew is detected.

        Args:
            image: Input image array.

        Returns:
            Tuple[np.ndarray, DeskewMetadata]: (deskewed_image, deskew_metadata)
        """
        gray = GrayscaleConverter.convert(image)
        angle, confidence, method = self.estimate_skew(gray)

        # Determine whether to rotate
        should_rotate = (
            confidence >= self.min_confidence
            and abs(angle) >= 0.25
            and abs(angle) <= self.max_angle
        )

        metadata = DeskewMetadata(
            rotation_angle=round(angle, 3),
            deskew_confidence=round(confidence, 3),
            was_rotated=should_rotate,
            method=method
        )

        if not should_rotate:
            return gray.copy(), metadata

        # Perform rotation
        h, w = gray.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(
            gray,
            rot_mat,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=255  # White background for documents
        )

        return deskewed, metadata
