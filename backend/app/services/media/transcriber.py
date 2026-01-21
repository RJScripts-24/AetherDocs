import logging
import os
from pathlib import Path
from typing import List, Dict, Any
from faster_whisper import WhisperModel

# Setup logger
logger = logging.getLogger(__name__)

class AudioTranscriber:
    """
    Wraps the Faster-Whisper library to convert audio into structured text.
    
    Key Features:
    1. Timestamp Preservation: Essential for the 'Strict Citations' feature.
    2. Model Caching: Loads weights from the mounted /models_cache volume.
    3. Hardware Acceleration: Automatically detects CUDA (GPU) vs CPU.
    """

    def __init__(self, model_size: str = "large-v3"):
        """
        Initialize the model.
        
        Args:
            model_size: 'tiny', 'base', 'small', 'medium', 'large-v3'.
                        'distil-large-v3' is also a good option for speed.
        """
        self.device = "cuda" if os.environ.get("USE_GPU", "false").lower() == "true" else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        # Path to the mounted volume for persistent model storage
        # This prevents re-downloading the 3GB model on every container restart
        cache_dir = os.environ.get("WHISPER_CACHE_DIR", "/app/models_cache/whisper")
        
        logger.info(f"Loading Whisper model '{model_size}' on {self.device} (compute: {self.compute_type})...")
        
        try:
            self.model = WhisperModel(
                model_size, 
                device=self.device, 
                compute_type=self.compute_type,
                download_root=cache_dir
            )
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.critical(f"Failed to load Whisper model: {e}")
            raise RuntimeError("Could not initialize ASR engine.") from e

    def transcribe(self, audio_path: Path) -> List[Dict[str, Any]]:
        """
        Performs the transcription.

        Args:
            audio_path: Path to the .mp3/.wav file.

        Returns:
            List of segments: [{'start': 0.0, 'end': 5.0, 'text': 'Hello world'}]
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Starting transcription for: {audio_path.name}")

        try:
            # beam_size=5 is standard for accuracy
            # vad_filter=True removes silence (crucial for lecture videos)
            segments, info = self.model.transcribe(
                str(audio_path), 
                beam_size=5, 
                vad_filter=True,
                language="en" # Enforce English for now, or make dynamic if needed
            )

            transcript_data = []
            
            # segments is a generator, so we iterate to consume and process
            for segment in segments:
                chunk = {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip()
                }
                transcript_data.append(chunk)

            logger.info(f"Transcription complete. Generated {len(transcript_data)} segments.")
            return transcript_data

        except Exception as e:
            logger.error(f"Transcription failed during processing: {e}")
            raise RuntimeError(f"Whisper processing failed: {e}")

    @staticmethod
    def format_as_text(transcript: List[Dict[str, Any]]) -> str:
        """
        Helper to convert the structured JSON back into a plain text block
        (useful if we just want raw text for the 'Common Book' base layer).
        """
        return " ".join([seg["text"] for seg in transcript])