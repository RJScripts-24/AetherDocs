import logging
import re
from typing import List, Dict
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)

class YouTubeTranscriptFetcher:
    """
    Fetches auto-generated or manual transcripts directly from YouTube.
    Uses youtube-transcript-api v1.2+ with the .fetch() method.
    """

    @staticmethod
    def extract_video_id(url: str) -> str:
        """
        Extract YouTube video ID from various URL formats.
        """
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
            r'embed\/([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {url}")

    def fetch_transcript(self, url: str) -> List[Dict]:
        """
        Fetch transcript from YouTube and format as Whisper-style segments.
        
        Returns:
            List of segments with format: [{"text": "...", "start": 0.0, "end": 5.0}, ...]
        """
        try:
            video_id = self.extract_video_id(url)
            logger.info(f"Fetching transcript for video ID: {video_id}")
            
            # v1.2+ API: use .fetch() instead of .get_transcript()
            ytt_api = YouTubeTranscriptApi()
            transcript_data = ytt_api.fetch(video_id)
            
            # Convert to Whisper-compatible format
            segments = []
            for entry in transcript_data:
                segments.append({
                    "text": entry.text,
                    "start": entry.start,
                    "end": entry.start + entry.duration
                })
            
            logger.info(f"Successfully fetched {len(segments)} transcript segments")
            return segments
            
        except Exception as e:
            logger.error(f"Failed to fetch transcript: {e}")
            raise RuntimeError(f"Transcript fetch failed: {str(e)}")
