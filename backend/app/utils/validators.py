import re
from uuid import UUID
from typing import Optional, Set

# Compiled regex for performance
# Supports:
# - standard: youtube.com/watch?v=...
# - short: youtu.be/...
# - embedded: youtube.com/embed/...
YOUTUBE_REGEX = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
)

# Allowed extensions mapped to the "Multimodal Ingestion Engine" spec
ALLOWED_EXTENSIONS: Set[str] = {
    # Documents
    '.pdf', '.docx', '.pptx',
    # Video
    '.mp4', '.mkv', '.mov', '.avi',
    # Audio
    '.mp3', '.wav', '.m4a'
}

def is_valid_youtube_url(url: str) -> bool:
    """
    Checks if a string is a valid single-video YouTube URL.
    Rejects playlists to prevent accidental bulk downloading.
    """
    if not url:
        return False
        
    # Check basic structure
    match = YOUTUBE_REGEX.match(url)
    if not match:
        return False
        
    # Explicitly reject playlist parameters to keep scope to single items
    if "list=" in url:
        return False
        
    return True

def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the unique 11-character video ID from a YouTube URL.
    Useful for deduplication or logging.
    """
    match = YOUTUBE_REGEX.match(url)
    if match:
        return match.group(5)
    return None

def is_supported_file_type(filename: str) -> bool:
    """
    Verifies if the uploaded file has a supported extension.
    Case-insensitive.
    """
    if not filename:
        return False
        
    # Get extension (last part after dot)
    parts = filename.rsplit('.', 1)
    if len(parts) < 2:
        return False
        
    ext = '.' + parts[1].lower()
    return ext in ALLOWED_EXTENSIONS

def validate_uuid(uuid_string: str) -> bool:
    """
    Validates if a string is a proper UUID (version 4).
    Security check for API endpoints receiving session IDs.
    """
    try:
        val = UUID(uuid_string, version=4)
        return str(val) == uuid_string
    except ValueError:
        return False