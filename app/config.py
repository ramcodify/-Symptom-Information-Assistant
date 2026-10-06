import os
from pathlib import Path
from typing import Dict
from pydantic import BaseModel, Field

class Settings(BaseModel):
    APP_NAME: str = "Medicine & Symptom Information Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    
    # Base paths
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    DATA_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data")
    
    # Optional External API Keys (graceful fallback if empty)
    OPENAI_API_KEY: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    TAVILY_API_KEY: str = Field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    OPENFDA_API_URL: str = "https://api.fda.gov/drug/label.json"
    
    # Standard Medical Disclaimer Text
    STANDARD_DISCLAIMER: str = (
        "⚠️ **Medical Disclaimer**: This assistant provides general educational and informational "
        "health content only and is NOT a substitute for professional clinical medical advice, "
        "diagnosis, or treatment. Always consult a licensed doctor, pharmacist, or qualified healthcare "
        "provider with any questions regarding medical conditions, medications, or symptoms. "
        "If you are experiencing a medical emergency, call your local emergency services (e.g. 911 / 112 / 999) immediately."
    )
    
    # Emergency Hotlines
    EMERGENCY_HOTLINES: Dict[str, Dict[str, str]] = {
        "US_CANADA": {"name": "Emergency Services (US & Canada)", "number": "911"},
        "EU_UK_INDIA": {"name": "Emergency Services (Europe / International)", "number": "112"},
        "UK": {"name": "Emergency Services (UK)", "number": "999"},
        "US_POISON": {"name": "US Poison Help Control", "number": "1-800-222-1222"},
        "US_CRISIS": {"name": "Suicide & Crisis Lifeline", "number": "988"},
        "AUSTRALIA": {"name": "Emergency Services (Australia)", "number": "000"}
    }

settings = Settings()
