import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Land Record Digitization & Validation System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "demo_secret_key_land_records_digitization_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./landrecords.db")
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./uploads")
    
    DEFAULT_OCR_ENGINE: str = os.getenv("DEFAULT_OCR_ENGINE", "tesseract_fallback")

    # Multi-level Explainable Confidence Engine Weights
    WEIGHT_OCR: float = 0.40
    WEIGHT_EXTRACTION: float = 0.30
    WEIGHT_VALIDATION: float = 0.20
    WEIGHT_CONTEXT: float = 0.10

    # Decision Thresholds
    CONFIDENCE_HIGH_THRESHOLD: float = 0.85
    CONFIDENCE_MEDIUM_THRESHOLD: float = 0.65

    class Config:
        case_sensitive = True

settings = Settings()
