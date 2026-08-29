import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
import math

class ImagePreprocessor:
    def __init__(self):
        pass

    def evaluate_quality(self, img_np: np.ndarray) -> dict:
        """
        Calculates resolution, Laplacian blur variance metric, contrast metric, skew angle, and noise level rating.
        """
        height, width = img_np.shape[:2]
        
        # Convert to grayscale if needed
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_np.copy()

        # 1. Blur metric via Laplacian variance
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        # 2. Contrast metric (standard deviation of pixel intensities)
        contrast = float(np.std(gray))
        
        # 3. Skew Angle Detection using Hough Lines
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
        
        skew_angle = 0.0
        if lines is not None:
            angles = []
            for line in lines:
                coords = line[0] if len(line.shape) > 1 else line
                x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                if -45 < angle < 45:
                    angles.append(angle)
            if angles:
                skew_angle = float(np.median(angles))

        # 4. Overall Quality Score computation (0.0 to 1.0)
        # Higher laplacian variance -> sharper image (threshold ~ 100 for decent text)
        blur_score = min(1.0, laplacian_var / 300.0)
        contrast_score = min(1.0, contrast / 80.0)
        skew_penalty = max(0.0, 1.0 - abs(skew_angle) / 10.0)
        
        quality_score = round(0.5 * blur_score + 0.3 * contrast_score + 0.2 * skew_penalty, 2)
        
        noise_level = "Low"
        if laplacian_var < 80 or contrast < 40:
            noise_level = "High"
        elif laplacian_var < 180:
            noise_level = "Medium"

        return {
            "quality_score": quality_score,
            "blur_metric": round(laplacian_var, 2),
            "contrast_metric": round(contrast, 2),
            "skew_angle": round(skew_angle, 2),
            "noise_level": noise_level,
            "width": width,
            "height": height
        }

    def process_image(self, input_path: str, output_path: str) -> dict:
        """
        Applies full image enhancement pipeline: Grayscale, Bilateral Filter, CLAHE, Deskew, and Binarization.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Load image with OpenCV
        img = cv2.imread(input_path)
        if img is None:
            # Fallback to PIL loading
            pil_img = Image.open(input_path).convert('RGB')
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        metrics = self.evaluate_quality(img)

        # 1. Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Deskew if skew angle > 0.5 degrees
        skew_angle = metrics["skew_angle"]
        if abs(skew_angle) > 0.5:
            (h, w) = gray.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
            gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        # 3. Noise reduction via Bilateral Filter (preserves text edges)
        denoised = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

        # 4. Adaptive Contrast Enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 5. Save enhanced preprocessed image
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, enhanced)

        return metrics

preprocessor = ImagePreprocessor()
