import base64
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

from groq import AsyncGroq, RateLimitError

from app.core.config import settings

# Setup logger
logger = logging.getLogger(__name__)

# Map file extensions to MIME types
MIME_TYPE_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}

class ImageDescriber:
    """
    Uses Llama-4-Scout to convert visual data (Charts, Graphs, Diagrams)
    into semantic text descriptions.
    
    This allows the Vector Store to index the *meaning* of a chart, 
    so users can ask "What is the trend in Figure 3?"
    """

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.warning("GROQ_API_KEY missing. Vision features will be disabled.")
            
        self.client = AsyncGroq(api_key=self.api_key)
        
        # Llama 4 Scout - Groq's recommended replacement for decommissioned llama-3.2-11b-vision
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct" 

    def _encode_image(self, image_path: Path) -> str:
        """
        Encodes a local image file to a base64 string required by the API.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _get_mime_type(self, image_path: Path) -> str:
        """
        Returns the correct MIME type based on the file extension.
        """
        ext = image_path.suffix.lower()
        return MIME_TYPE_MAP.get(ext, "image/png")

    async def describe_image(self, image_path: Path) -> str:
        """
        Generates a dense textual description of the image.
        
        Args:
            image_path: Path to the extracted .png/.jpg file.
            
        Returns:
            String description focusing on data points, trends, and labels.
        """
        if not image_path.exists():
            return "[Error: Image file not found]"

        base64_image = self._encode_image(image_path)
        mime_type = self._get_mime_type(image_path)
        
        # System prompt to force the AI to be analytical, not artistic
        prompt = (
            "Analyze this image. It is likely a chart, graph, or educational diagram. "
            "Provide a detailed textual description of the data, trends, axis labels, "
            "and relationships shown. Do not describe the colors or style. "
            "Focus purely on the information content."
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending image {image_path.name} ({mime_type}) to Llama-4-Scout (attempt {attempt + 1})...")
                
                chat_completion = await self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    model=self.model,
                    temperature=0.1,  # strict factual description
                    max_completion_tokens=1024,
                )

                description = chat_completion.choices[0].message.content
                logger.info(f"Vision analysis succeeded for {image_path.name}")
                return f"[VISUAL DATA DESCRIPTION]: {description}"

            except RateLimitError:
                wait_time = (2 ** attempt) * 3  # 3s, 6s, 12s
                logger.warning(f"Groq Vision Rate Limit Hit (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Vision analysis failed for {image_path.name}: {e}")
                return f"[Description Unavailable: {e}]"
        
        logger.error(f"Vision analysis for {image_path.name}: All retries exhausted.")
        return "[Description Unavailable: Rate Limit - All retries exhausted]"