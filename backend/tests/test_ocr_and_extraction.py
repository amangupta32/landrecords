from app.services.ocr import OCRManager, FallbackLandRecordOCRProvider
from app.services.extraction import field_extractor

def test_ocr_fallback_provider():
    provider = FallbackLandRecordOCRProvider()
    res = provider.extract_text_and_boxes("uploads/jamabandi_rampur_2024.pdf")
    
    assert "full_text" in res
    assert "word_boxes" in res
    assert res["base_ocr_confidence"] > 0.80

def test_ocr_manager_digit_normalization():
    raw_devnagari = "खसरा संख्या: २४५/१, कुल क्षेत्रफल: ४.२५ एकड़"
    normalized = OCRManager.normalize_text(raw_devnagari)
    
    assert "245/1" in normalized
    assert "4.25" in normalized

def test_field_extractor():
    text = "अधिकार अभिलेख (जमाबंदी) खातेदार का नाम: Ramesh Kumar Sharma (रमेश कुमार शर्मा) खसरा संख्या: २४५/१ Land Area: 4.25 Acres Village: Rampur"
    norm = OCRManager.normalize_text(text)
    
    extracted = field_extractor.extract_fields(text, norm)
    
    assert "Ramesh Kumar Sharma" in extracted["owner_name"]["value"] or "रमेश" in extracted["owner_name"]["value"]
    assert extracted["khasra_number"]["value"] == "245/1"
    assert extracted["land_area"]["value"] == 4.25
    assert extracted["village"]["value"] == "Rampur"
