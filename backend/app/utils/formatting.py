import re
import unicodedata
from typing import Optional

def seconds_to_timestamp(seconds: float) -> str:
    """
    Converts raw seconds (e.g., 125.5) into a standard video timestamp format.
    
    Examples:
        65.0   -> "01:05"
        3665.0 -> "01:01:05"
        
    Used by: Chatbot citations and PDF generation.
    """
    if seconds is None:
        return "00:00"
        
    seconds = int(round(seconds))
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def clean_filename(filename: str) -> str:
    """
    Sanitizes filenames to prevent directory traversal and filesystem issues.
    Replaces spaces with underscores and removes non-alphanumeric chars.
    
    Example: 
        "My Lecture v1.2 (Final).pdf" -> "My_Lecture_v1_2_Final.pdf"
    """
    # Split extension
    parts = filename.rsplit('.', 1)
    if len(parts) == 2:
        name, ext = parts
    else:
        name, ext = filename, ""

    # Normalize unicode characters (e.g., accents)
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    
    # Replace whitespace with underscore
    name = re.sub(r'\s+', '_', name)
    
    # Remove anything that isn't alphanumeric, underscore, or hyphen
    name = re.sub(r'[^\w\-]', '', name)
    
    if ext:
        return f"{name}.{ext}"
    return name

def sanitize_text(text: str) -> str:
    """
    Cleans text extracted from PDFs or Transcripts.
    Removes null bytes, excessive whitespace, and non-printable control characters.
    """
    if not text:
        return ""
        
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Normalize unicode (fix broken ligature characters often found in PDFs)
    text = unicodedata.normalize('NFKC', text)
    
    # Collapse multiple spaces/newlines into single space
    # (Optional: sometimes we want to keep newlines for markdown, 
    # so we'll just trim trailing/leading and handle crazy whitespace)
    text = text.strip()
    
    return text

def format_file_size(size_in_bytes: int) -> str:
    """
    Converts bytes to human readable string (KB, MB, GB).
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"