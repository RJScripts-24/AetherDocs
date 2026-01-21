import subprocess
import logging
import shutil
from pathlib import Path
from typing import Optional

# Setup logger
logger = logging.getLogger(__name__)

class MediaConverter:
    """
    Wraps FFMPEG system calls to handle media normalization and audio extraction.
    Ensures all inputs (MP4, MKV, MP3, WAV) are converted to a standard 
    format optimized for the Whisper model (16kHz, Mono).
    """

    def __init__(self):
        # Verify ffmpeg is installed in the container
        if not shutil.which("ffmpeg"):
            raise RuntimeError("FFmpeg binary not found. Ensure it is installed in the Docker container.")

    @staticmethod
    def extract_audio(
        input_path: Path, 
        output_path: Path, 
        sample_rate: int = 16000,
        bitrate: str = "32k"
    ) -> Path:
        """
        Extracts audio track from a video file or normalizes an existing audio file.
        
        Args:
            input_path: Path to the source file (e.g., 'upload.mp4').
            output_path: Target path for the clean audio (e.g., 'audio.mp3').
            sample_rate: Target sample rate (default 16kHz is optimal for Whisper).
            bitrate: Target bitrate (Low bitrate is fine for speech, saves processing time).
            
        Returns:
            Path: The path to the generated audio file.
            
        Raises:
            RuntimeError: If FFMPEG processing fails.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input media file not found: {input_path}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # FFmpeg command construction
        # -y: Overwrite output files without asking
        # -i: Input file
        # -vn: Disable video recording (extract audio only)
        # -acodec: Audio codec (libmp3lame for mp3)
        # -ac: Audio channels (1 for Mono - Whisper mixes down anyway, saves space)
        # -ar: Audio sampling rate (16000 Hz)
        # -ab: Audio bitrate
        command = [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-vn",
            "-acodec", "libmp3lame",
            "-ac", "1", 
            "-ar", str(sample_rate),
            "-ab", bitrate,
            str(output_path)
        ]

        logger.info(f"Starting FFMPEG conversion: {input_path.name} -> {output_path.name}")

        try:
            # Run FFMPEG as a subprocess
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info(f"Conversion successful: {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            logger.error(f"FFMPEG failed with error: {e.stderr}")
            raise RuntimeError(f"Media conversion failed: {e.stderr}") from e

    @staticmethod
    def get_media_metadata(file_path: Path) -> dict:
        """
        Uses ffprobe to extract duration and format metadata.
        Useful for estimating processing time.
        """
        if not shutil.which("ffprobe"):
            logger.warning("ffprobe not found, skipping metadata extraction.")
            return {}

        command = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration,size",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
            output = result.stdout.strip().split()
            
            if len(output) >= 1:
                return {
                    "duration_seconds": float(output[0]),
                    # size is usually available via os.stat, but good to have stream size
                }
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
        
        return {}