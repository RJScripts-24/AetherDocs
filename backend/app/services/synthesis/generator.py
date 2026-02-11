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
        Includes exponential backoff for rate limits and TPM limits.
        """
        model = self._get_model_name(mode)
        max_retries = 5
        
        # Cap max_tokens to stay within Groq free-tier TPM (6000 tokens/min)
        # Reserve tokens for input — cap output at 4000 tokens max
        safe_max_tokens = min(max_tokens, 4000)
        
        # Auto-truncate prompt if it's too large (~4 chars per token rough estimate)
        # Keep input under ~2000 tokens (8000 chars) so input+output < 6000 TPM
        max_prompt_chars = 8000
        if len(user_prompt) > max_prompt_chars:
            logger.warning(f"Prompt too large ({len(user_prompt)} chars). Truncating to {max_prompt_chars} chars.")
            user_prompt = user_prompt[:max_prompt_chars] + "\n\n[Content truncated for processing limits]"
        
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
                    max_tokens=safe_max_tokens,
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
                error_str = str(e)
                # Treat 413 (TPM exceeded) as a retryable rate limit
                if "413" in error_str or "rate_limit" in error_str.lower() or "too large" in error_str.lower():
                    wait_time = (2 ** attempt) * 10  # 10s, 20s, 40s, 80s — longer waits for TPM
                    logger.warning(f"Groq TPM limit hit (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Groq API Error: {e}")
                    raise RuntimeError(f"LLM Generation failed: {e}")
        
        # All retries exhausted
        logger.error("Groq Rate/TPM Limit: All retries exhausted. Returning empty.")
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
            temperature=0.3,  # Lower temp for more factual summaries
            max_tokens=4096   # Detailed summary to avoid losing nuance
        )