"""FastAPI router for Land Record AI digitization endpoints."""

import io
import os
from typing import Any, Dict, Optional
import cv2
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
import numpy as np
from PIL import Image

from pipeline import LandRecordAIPipeline
from schemas.fields import ExtractedFields
from schemas.ocr import OCREngineResult
from schemas.output import DocumentProcessingOutput

router = APIRouter(prefix="/api/v1", tags=["Land Record AI Pipeline"])

# Singleton pipeline instance
_pipeline: Optional[LandRecordAIPipeline] = None


def get_pipeline() -> LandRecordAIPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = LandRecordAIPipeline()
    return _pipeline


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint returning system status and available OCR engines."""
    p = get_pipeline()
    return {
        "status": "healthy",
        "service": "land-record-ai",
        "available_ocr_engines": p.ocr_router.get_available_engines(),
        "default_language": "hin+eng"
    }


@router.post("/process", response_model=DocumentProcessingOutput)
async def process_document(
    file: UploadFile = File(...),
    preferred_engine: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default=None),
    is_handwritten: bool = Form(default=False)
) -> DocumentProcessingOutput:
    """
    Process an uploaded land record document through full AI pipeline:
    Preprocessing -> Multi-Engine OCR -> Hybrid NLP Extraction -> Validation -> Explainable Confidence.
    """
    p = get_pipeline()

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        # Decode image using PIL
        image_stream = io.BytesIO(contents)
        pil_img = Image.open(image_stream).convert("RGB")
        img_np = np.array(pil_img)
        # Convert RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode image: {str(e)}")

    doc_id = os.path.splitext(file.filename or "doc")[0]
    result = p.process(
        image=img_bgr,
        document_id=doc_id,
        preferred_engine=preferred_engine,
        language=language,
        is_handwritten=is_handwritten
    )

    return result


@router.post("/ocr", response_model=OCREngineResult)
async def run_ocr(
    file: UploadFile = File(...),
    preferred_engine: Optional[str] = Form(default=None),
    language: Optional[str] = Form(default=None)
) -> OCREngineResult:
    """Run OCR stage only on an uploaded document image."""
    p = get_pipeline()
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    try:
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
        img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image decoding failed: {str(e)}")

    preproc = p.preprocessing.process(img_bgr)
    ocr_result, _ = p.ocr_router.recognize(
        preproc.processed_image,
        preferred_engine=preferred_engine,
        language=language
    )
    return ocr_result


@router.post("/validate")
async def run_validation(fields: ExtractedFields) -> Dict[str, Any]:
    """Validate extracted fields against state revenue rules and format checks."""
    p = get_pipeline()
    report = p.validation.validate(fields)
    return report.model_dump()
