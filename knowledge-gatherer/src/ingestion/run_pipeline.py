import logging
from src.ingestion.config import Config
from src.ingestion.api_clients.youtube_client import YouTubeMultimodalClient
from src.ingestion.storage.gcs_manager import GCSManager

logger = logging.getLogger("Pipeline_Orchestrator")

def run_knowledge_gatherer():
    logger.info("=== Starting Knowledge Gatherer Pipeline ===")

    youtube_client = YouTubeMultimodalClient()
    gcs_manager = GCSManager()

    # 1. Process and Upload YouTube Insights
    for video in Config.SEED_YOUTUBE_VIDEOS:
        result = youtube_client.analyze_video(video)
        
        if result["status"] == "success":
            filename = f"insight_{result['type']}_{result['video_id']}.md"
            gcs_manager.upload_text(filename, result["extracted_markdown"])
        else:
            logger.warning(f"Skipping upload for {result.get('video_id')} due to processing failure.")

    # 2. Upload Local PDFs (e.g., Legal documents, NITI Aayog reports)
    logger.info("Initiating local PDF upload sequence...")
    gcs_manager.upload_local_pdfs()

    logger.info("=== Pipeline Execution Complete. Data ready for Vertex AI Agent Builder. ===")

if __name__ == "__main__":
    run_knowledge_gatherer()