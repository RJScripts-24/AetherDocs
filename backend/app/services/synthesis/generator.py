import logging
import asyncio
import os
from typing import Optional
from groq import AsyncGroq, RateLimitError, APIError

from app.core.config import settings
from app.schemas.ingestion import IntelligenceMode

# Setup logger
logger = logging.getLogger(__name__)

class LLMClient:
    """
    Wraps the Groq Cloud API for ultra-low latency inference.
    
    Responsibilities:
    1. Model Routing: Swaps between 8b (Fast) and 70b (Deep) based on user selection.
    2. Async Execution: Handles parallel chunk processing for the Fusion Engine.
    3. Resilience: Basic retry logic for rate limits.
    """

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found. LLM features will fail.")
        
        # Initialize the asynchronous client
        self.client = AsyncGroq(api_key=self.api_key)

    def _get_model_name(self, mode: IntelligenceMode) -> str:
        """
        Maps the abstract 'Intelligence Mode' to specific Groq model IDs.
        """
        if mode == IntelligenceMode.DEEP:
            # High intelligence, larger context, slower
            return "llama-3.3-70b-versatile" 
        else:
            # Ultra-fast, lower latency
            return "llama-3.1-8b-instant"

    async def generate_text(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        mode: IntelligenceMode = IntelligenceMode.FAST,
        temperature: float = 0.5,
        max_tokens: int = 2048
    ) -> str:
        """
        Generates text using the specified Llama-3 model.
        Includes exponential backoff for rate limits.
        """
        model = self._get_model_name(mode)
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                chat_completion = await self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        }
                    ],
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1,
                    stop=None,
                    stream=False,
                )
                
                return chat_completion.choices[0].message.content

            except RateLimitError:
                wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s, 16s, 32s
                logger.warning(f"Groq Rate Limit hit (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except APIError as e:
                logger.error(f"Groq API Error: {e}")
                raise RuntimeError(f"LLM Generation failed: {e}")
        
        # All retries exhausted
        logger.error("Groq Rate Limit: All retries exhausted. Returning empty.")
        return ""

    async def generate_summary(self, text: str, mode: IntelligenceMode) -> str:
        """
        Specialized helper for summarizing large blocks of text (Transcript/Base Layer).
        """
        system = (
            "You are an expert summarizer. "
            "Condense the following text into a dense, high-level narrative summary. "
            "Capture the key themes, chronological flow, and main arguments. "
            "Do not lose technical details."
        )
        
        # We truncate text to roughly fit the context window if it's massive
        # 8192 tokens approx 30k chars. Safe buffer 25k.
        safe_text = text[:25000] 
        
        return await self.generate_text(
            system_prompt=system,
            user_prompt=safe_text,
            mode=mode,
            temperature=0.3 # Lower temp for more factual summaries
        )