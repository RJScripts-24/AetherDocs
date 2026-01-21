import base64
import logging
import os
from pathlib import Path
from typing import Optional

from groq import AsyncGroq, RateLimitError

from app.core.config import settings

# Setup logger
logger = logging.getLogger(__name__)

class ImageDescriber:
    """
    Uses Llama-3.2-Vision to convert visual data (Charts, Graphs, Diagrams)
    into semantic text descriptions.
    
    This allows the Vector Store to index the *meaning* of a chart, 
    so users can ask "What is the trend in Figure 3?"
    """

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.warning("GROQ_API_KEY missing. Vision features will be disabled.")
            
        self.client = AsyncGroq(api_key=self.api_key)
        
        # Specific model optimized for vision tasks on Groq
        self.model = "llama-3.2-11b-vision-preview" 

    def _encode_image(self, image_path: Path) -> str:
        """
        Encodes a local image file to a base64 string required by the API.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

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
        
        # System prompt to force the AI to be analytical, not artistic
        prompt = (
            "Analyze this image. It is likely a chart, graph, or educational diagram. "
            "Provide a detailed textual description of the data, trends, axis labels, "
            "and relationships shown. Do not describe the colors or style. "
            "Focus purely on the information content."
        )

        try:
            logger.info(f"Sending image {image_path.name} to Llama-Vision...")
            
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model=self.model,
                temperature=0.1, # strict factual description
                max_tokens=1024,
            )

            description = chat_completion.choices[0].message.content
            return f"[VISUAL DATA DESCRIPTION]: {description}"

        except RateLimitError:
            logger.warning("Groq Vision Rate Limit Hit. Skipping image.")
            return "[Description Unavailable: Rate Limit]"
            
        except Exception as e:
            logger.error(f"Vision analysis failed for {image_path.name}: {e}")
            return "[Description Unavailable: Processing Error]"