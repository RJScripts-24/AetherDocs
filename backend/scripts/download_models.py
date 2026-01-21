import os
import logging
import shutil
from pathlib import Path
from faster_whisper import download_model
from chromadb.utils import embedding_functions

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define Target Directories
# These should match the volume mounts in docker-compose
WHISPER_CACHE_DIR = os.getenv("WHISPER_CACHE_DIR", "/app/models_cache/whisper")
SENTENCE_TRANSFORMERS_CACHE = os.getenv("SENTENCE_TRANSFORMERS_HOME", "/app/models_cache/embeddings")

def download_whisper_models():
    """
    Downloads the Faster-Whisper models.
    We download both 'distil-large-v3' (Fast Mode) and 'large-v3' (Deep Mode).
    """
    models_to_fetch = ["distil-large-v3", "large-v3"]
    
    logger.info(f"Target Whisper Cache Dir: {WHISPER_CACHE_DIR}")
    
    for model_name in models_to_fetch:
        logger.info(f"Downloading Whisper model: {model_name}...")
        try:
            # this function returns the path to the downloaded model
            path = download_model(model_name, output_dir=WHISPER_CACHE_DIR)
            logger.info(f"✓ {model_name} downloaded to {path}")
        except Exception as e:
            logger.error(f"Failed to download {model_name}: {e}")
            raise e

def download_embedding_models():
    """
    Downloads the SentenceTransformer model used by ChromaDB.
    Standard model: 'all-MiniLM-L6-v2' (Small, Fast, Good enough for RAG)
    """
    model_name = "all-MiniLM-L6-v2"
    
    logger.info(f"Target Embedding Cache Dir: {SENTENCE_TRANSFORMERS_CACHE}")
    logger.info(f"Downloading Embedding model: {model_name}...")

    try:
        # We assume the standard HuggingFace cache structure.
        # Initializing the function triggers the download if not present.
        # We set the cache folder environment variable specifically for this process.
        os.environ["SENTENCE_TRANSFORMERS_HOME"] = SENTENCE_TRANSFORMERS_CACHE
        
        # Trigger download
        embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
        
        logger.info(f"✓ {model_name} ready.")
    except Exception as e:
        logger.error(f"Failed to download embedding model: {e}")
        raise e

def main():
    logger.info("--- Starting Model Pre-fetch ---")
    
    # Ensure directories exist
    Path(WHISPER_CACHE_DIR).mkdir(parents=True, exist_ok=True)
    Path(SENTENCE_TRANSFORMERS_CACHE).mkdir(parents=True, exist_ok=True)

    download_whisper_models()
    download_embedding_models()
    
    logger.info("--- All Models Downloaded Successfully ---")

if __name__ == "__main__":
    main()