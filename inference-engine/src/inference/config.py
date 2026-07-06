import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Inference_Config")

load_dotenv()

class InferenceConfig:
    # Core GCP Configuration
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "project-ef9af33d-cdd2-48a3-8a3")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Vertex AI Knowledge Graph Datastore (Phase 1 Output)
    USE_VERTEX_DATASTORE = os.getenv("USE_VERTEX_DATASTORE", "true").lower() == "true"
    VERTEX_DATASTORE_ID = os.getenv("VERTEX_DATASTORE_ID", "knowledge-ivestment-coach_1783345303816")
    DATASTORE_LOCATION = os.getenv("DATASTORE_LOCATION", "us")
    
    # Agent Garden: Deployed Junior Financial Advisor Configuration
    FINANCIAL_PROJECT_ID = os.getenv("FINANCIAL_PROJECT_ID", "1024837079557")
    FINANCIAL_AGENT_ID = os.getenv("FINANCIAL_AGENT_ID", "7989085022525063168")
    FINANCIAL_LOCATION = os.getenv("FINANCIAL_LOCATION", "us-central1")
    
    # Model Core Routing Strategy
    FAST_MODEL = "gemini-2.5-flash"      # Ultra-fast synthesis and critique loops
    REASONING_MODEL = "gemini-1.5-pro"   # Deep planning for heavy tool processing

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            logger.warning("WARNING: GEMINI_API_KEY is not set. Local fallback required.")
        logger.info("Inference Configuration successfully loaded.")

InferenceConfig.validate()