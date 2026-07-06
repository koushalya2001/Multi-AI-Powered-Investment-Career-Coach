import logging
import os
from pathlib import Path
from google.cloud import storage
from src.ingestion.config import Config

logger = logging.getLogger("GCS_Manager")

class GCSManager:
    """Handles secure uploads to Google Cloud Storage for Vertex AI indexing."""
    
    def __init__(self):
        # Uses Application Default Credentials (ADC)
        self.storage_client = storage.Client(project=Config.PROJECT_ID)
        self.bucket = self.storage_client.bucket(Config.GCS_BUCKET_NAME)

    def upload_text(self, filename: str, content: str):
        """Uploads generated markdown insights to GCS."""
        try:
            blob = self.bucket.blob(f"youtube_insights/{filename}")
            blob.upload_from_string(content, content_type="text/markdown")
            logger.info(f"Uploaded insight: gs://{Config.GCS_BUCKET_NAME}/youtube_insights/{filename}")
        except Exception as e:
            logger.error(f"GCS Upload failed for text {filename}: {e}")

    def upload_local_pdfs(self):
        """Iterates through the local PDF directory and uploads them to GCS."""
        pdf_dir = Path(Config.LOCAL_PDF_DIRECTORY)
        
        if not pdf_dir.exists() or not pdf_dir.is_dir():
            logger.warning(f"PDF directory {pdf_dir} not found. Skipping PDF upload.")
            return

        for pdf_path in pdf_dir.glob("*.pdf"):
            try:
                blob = self.bucket.blob(f"legal_policy_docs/{pdf_path.name}")
                blob.upload_from_filename(str(pdf_path), content_type="application/pdf")
                logger.info(f"Uploaded PDF: gs://{Config.GCS_BUCKET_NAME}/legal_policy_docs/{pdf_path.name}")
            except Exception as e:
                logger.error(f"Failed to upload PDF {pdf_path.name}: {e}")