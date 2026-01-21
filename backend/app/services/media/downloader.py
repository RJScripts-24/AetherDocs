import logging
import yt_dlp
from pathlib import Path
from typing import Optional
from uuid import UUID

# Setup logger
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """
    Handles the ingestion of YouTube content via yt-dlp.
    Optimized for the 'Burner' architecture:
    1. Downloads directly to the specific /tmp/{session_id} directory.
    2. Prioritizes 'bestaudio' to save bandwidth (since we need the transcript).
    3. Handles retries and specific YouTube errors.
    """

    def __init__(self):
        # Common headers to avoid bot detection
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

    def download(self, url: str, output_dir: Path, session_id: UUID) -> Path:
        """
        Downloads the audio stream from a YouTube URL.

        Args:
            url: The YouTube URL.
            output_dir: The session-specific /tmp directory.
            session_id: For logging context.

        Returns:
            Path: The file path to the downloaded media.
        
        Raises:
            RuntimeError: If download fails after retries.
        """
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Output template: /tmp/{uuid}/{video_id}.{ext}
        output_template = str(output_dir / "%(id)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',  # Fetch best audio directly to speed up transcription pipeline
            'outtmpl': output_template,
            'noplaylist': True,          # Strictly single video processing
            'quiet': True,               # Reduce noise, we use custom logging
            'no_warnings': True,
            'user_agent': self.user_agent,
            # Post-processors to ensure we get a clean file container
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        logger.info(f"[{session_id}] Starting YouTube download: {url}")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 1. Extract info to get metadata/filename before downloading
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get('title', 'Unknown Title')
                video_id = info_dict.get('id', 'video')
                
                logger.info(f"[{session_id}] Found video: '{video_title}' (ID: {video_id})")

                # 2. Perform the actual download
                error_code = ydl.download([url])
                
                if error_code != 0:
                    raise RuntimeError(f"yt-dlp returned error code {error_code}")

                # 3. Construct the expected output path
                # Note: valid because we forced mp3 conversion in postprocessors
                expected_filename = f"{video_id}.mp3"
                final_path = output_dir / expected_filename

                if not final_path.exists():
                    # Fallback search if yt-dlp naming convention varies slightly
                    found_files = list(output_dir.glob(f"{video_id}*"))
                    if found_files:
                        final_path = found_files[0]
                    else:
                        raise FileNotFoundError(f"Download reported success but file missing: {final_path}")

                logger.info(f"[{session_id}] Download completed: {final_path} ({final_path.stat().st_size / 1024 / 1024:.2f} MB)")
                return final_path

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"[{session_id}] YouTube Download Error: {str(e)}")
            raise RuntimeError(f"Failed to download video: {str(e)}")
        except Exception as e:
            logger.error(f"[{session_id}] Unexpected error in downloader: {str(e)}")
            raise RuntimeError(f"Internal downloader error: {str(e)}")