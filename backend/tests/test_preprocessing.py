import numpy as np
import pytest
from app.services.preprocessing import preprocessor

def test_evaluate_quality():
    # Create synthetic grayscale image
    img = np.zeros((300, 400, 3), dtype=np.uint8)
    # Draw sharp white box
    img[100:200, 100:300] = 255
    
    metrics = preprocessor.evaluate_quality(img)
    assert "quality_score" in metrics
    assert "blur_metric" in metrics
    assert "contrast_metric" in metrics
    assert metrics["width"] == 400
    assert metrics["height"] == 300
