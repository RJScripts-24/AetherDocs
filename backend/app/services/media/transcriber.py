import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from app.core.config import settings

# Only import faster_whisper if we need it (lazy load to speed up cloud-only mode)
# But for type hints/compatibility we might need to handle imports carefully.
# We'll import inside the class if falling back to local.

# Setup logger
logger = logging.getLogger(__name__)

class AudioTranscriber:
    """
    Hybrid Transcriber:
    - Uses Groq Cloud API (Blazing Fast) if GROQ_API_KEY is present.
    - Falls back to Local Faster-Whisper (Private/Offline) if no key found.
    """

    def __init__(self, model_size: str = "large-v3"):
        """
        Initialize the transcription engine.
        Prioritizes Cloud API for speed.
        """
        self.groq_api_key = settings.GROQ_API_KEY
        self.use_cloud = bool(self.groq_api_key and GROQ_AVAILABLE)
        
        if self.use_cloud:
            logger.info("🚀 GROQ_API_KEY found. Using Groq Cloud for ultra-fast transcription.")
            self.client = Groq(api_key=self.groq_api_key)
            self.model_id = "whisper-large-v3" # Groq's fastest/best model
            
            # We don't load the local model here, saving RAM and startup time!
        else:
            logger.info("☁️ GROQ_API_KEY not found. Fallback to Local Whisper (slower but private).")
            
            from faster_whisper import WhisperModel
            
            self.device = "cuda" if os.environ.get("USE_GPU", "false").lower() == "true" else "cpu"
            self.compute_type = "float16" if self.device == "cuda" else "int8"
            
            cache_dir = os.environ.get("WHISPER_CACHE_DIR", "/app/models_cache/whisper")
            
            logger.info(f"Loading Local Whisper '{model_size}' on {self.device}...")
            try:
                self.model = WhisperModel(
                    model_size, 
                    device=self.device, 
                    compute_type=self.compute_type,
                    download_root=cache_dir
                )
                logger.info("Local Whisper loaded successfully.")
            except Exception as e:
                logger.critical(f"Failed to load Whisper: {e}")
                raise RuntimeError("Could not initialize ASR engine.") from e

    def transcribe(self, audio_path: Path) -> List[Dict[str, Any]]:
        """
        Performs transcription (Cloud or Local).
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"File not found: {audio_path}")

        if self.use_cloud:
            return self._transcribe_cloud(audio_path)
        else:
            return self._transcribe_local(audio_path)

    def _transcribe_cloud(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts audio and sends to Groq API.
        """
        logger.info(f"Uploading {file_path.name} to Groq Cloud...")
        
        # 1. Check file size. Groq limit is ~25MB.
        # If it's a video, we MUST extract audio to compress it.
        # If it's audio but large, we might need to compress.
        
        # Use a temp file for the extracted audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
            tmp_audio_path = Path(tmp_audio.name)
        
        try:
            # 2. Extract Audio with FFmpeg (Force re-encoding to MP3 to ensure size < 25MB)
            # -vn: no video
            # -ar 16000: 16khz (Whisper native)
            # -ac 1: mono
            # -b:a 64k: low bitrate (perfect for speech, keeps file tiny)
            cmd = [
                "ffmpeg", "-y", "-i", str(file_path),
                "-vn", "-ar", "16000", "-ac", "1", "-b:a", "64k",
                str(tmp_audio_path)
            ]
            
            # Suppress ffmpeg logs unless error
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            
            filesize_mb = tmp_audio_path.stat().st_size / (1024 * 1024)
            logger.info(f"Extracted audio size: {filesize_mb:.2f} MB")
            
            if filesize_mb > 25:
                # Fallback or error? For now, risk it or error.
                # 64kbps MP3 is ~0.5MB/min. 25MB = 50 minutes.
                if filesize_mb > 25:
                     logger.warning("Audio > 25MB. Groq might reject. Proceeding anyway...")

            # 3. Call API
            with open(tmp_audio_path, "rb") as file_obj:
                transcription = self.client.audio.transcriptions.create(
                    file=(tmp_audio_path.name, file_obj.read()),
                    model=self.model_id,
                    response_format="verbose_json",
                    temperature=0.0
                )
            
            # 4. Parse Response matches interface
            # transcription is a customized object, likely has .segments
            segments = transcription.segments
            transcript_data = []
            
            for segment in segments:
                # Groq returns dict or object? Python client usually returns object with attributes
                # But verbose_json might play differently. Let's assume object access.
                chunk = {
                    "start": round(segment['start'], 2) if isinstance(segment, dict) else round(segment.start, 2),
                    "end": round(segment['end'], 2) if isinstance(segment, dict) else round(segment.end, 2),
                    "text": (segment['text'] if isinstance(segment, dict) else segment.text).strip()
                }
                transcript_data.append(chunk)
                
            logger.info(f"Cloud Transcription Complete: {len(transcript_data)} segments.")
            return transcript_data

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg extraction failed: {e.stderr.decode()}")
            raise RuntimeError("Could not extract audio for cloud processing.")
        except Exception as e:
            logger.error(f"Groq Cloud Error: {e}")
            raise RuntimeError(f"Cloud transcription failed: {e}")
        finally:
            # Cleanup temp file
            if tmp_audio_path.exists():
                tmp_audio_path.unlink()

    def _transcribe_local(self, audio_path: Path) -> List[Dict[str, Any]]:
        """
        Original Faster-Whisper logic.
        """
        logger.info(f"Starting local transcription for: {audio_path.name}")
        try:
            segments, info = self.model.transcribe(
                str(audio_path), 
                beam_size=5, 
                vad_filter=True,
                language="en"
            )

            transcript_data = []
            for segment in segments:
                chunk = {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip()
                }
                transcript_data.append(chunk)

            logger.info(f"Local Transcription complete. Generated {len(transcript_data)} segments.")
            return transcript_data

        except Exception as e:
            logger.error(f"Local Transcription failed: {e}")
            raise RuntimeError(f"Whisper processing failed: {e}")

    @staticmethod
    def format_as_text(transcript: List[Dict[str, Any]]) -> str:
        """
        Helper to convert the structured JSON back into a plain text block.
        """
        return " ".join([seg["text"] for seg in transcript])