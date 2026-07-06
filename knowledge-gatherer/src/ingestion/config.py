import os
import logging
from dotenv import load_dotenv
from pathlib import Path
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("KnowledgeGatherer_Config")

load_dotenv()
# --- THE BULLETPROOF PATH FIX ---
# This finds the exact absolute path of the folder containing config.py (src/ingestion/)
BASE_DIR = Path(__file__).resolve().parent 
# This safely appends "data/pdfs" to it, no matter where the script is executed from
DEFAULT_PDF_DIR = str(BASE_DIR / "data" / "pdfs")

class Config:
    """Centralized configuration manager ensuring fail-fast startup."""
    
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
    REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1") # Vertex AI needs a region
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LOCAL_PDF_DIRECTORY = os.getenv("LOCAL_PDF_DIRECTORY", DEFAULT_PDF_DIR)

    PROMPT_BUSINESS_VIDEO = (
        "You are a senior data analyst. Analyze this video transcript/content. "
        "Extract the core arguments, and specifically transcribe data from any charts "
        "or economic trends mentioned. Output in clean Markdown with headers: "
        "'Core Thesis', 'Extracted Data Points', 'Key Risk Factors', 'Key Expert Recommendation', 'Key Patterns/Trends observed to justify recommendations'."
    )
    
    PROMPT_CAREER_VIDEO = (
        "You are an expert career strategist. Analyze this video to identify emerging workforce trends. "
        "Extract: 1. Skills rising in demand. 2. Roles susceptible to AI automation. 3. Growth industries. "
        "Provide actionable, concise intelligence in Markdown format."
    )

    SEED_YOUTUBE_VIDEOS = [
        {"id": "l6d_0PB0Pbg", "type": "career"}, 
        {"id": "oDO_hTtQedQ", "type": "career"},
        {"id": "WT8qxZBvZSw", "type": "business"},
        {"id": "FLppjVgusHE", "type": "business"}
    ]

    @classmethod
    def validate(cls):
        missing = [k for k in ["PROJECT_ID", "REGION", "GCS_BUCKET_NAME"] if not getattr(cls, k)]
        if missing:
            raise ValueError(f"CRITICAL: Missing environment variables: {', '.join(missing)}")
        logger.info("Configuration validated successfully.")

Config.validate()