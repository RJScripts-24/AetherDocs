import logging
import asyncio
from typing import List, Dict, Optional
from uuid import UUID

from app.services.synthesis.generator import LLMClient
from app.schemas.ingestion import IntelligenceMode

# Setup logger
logger = logging.getLogger(__name__)

class FusionEngine:
    """
    Implements the 'Smart Deduplication' logic.
    
    The Algorithm:
    1. Define S_base (Primary Source) usually the Video Transcript.
    2. Define S_secondary (Secondary Source) usually PDF/Textbooks.
    3. Iterate through S_secondary chunks.
    4. Perform Semantic Subtraction: New_Info = Chunk - S_base.
    5. S_final = S_base + New_Info.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
        # Load the specialized system prompt for deduplication
        # This prompt teaches the LLM to act as a "Logical Difference Engine"
        try:
            with open("app/templates/prompts/deduplication.txt", "r") as f:
                self.system_prompt_template = f.read()
        except FileNotFoundError:
            # Fallback if file not found (mostly for dev safety)
            logger.warning("deduplication.txt not found, using hardcoded fallback.")
            self.system_prompt_template = (
                "You are a Difference Engine. Compare the 'New Text' against the 'Known Context'. "
                "Extract ONLY facts/formulas/nuances present in 'New Text' that are MISSING from 'Known Context'. "
                "If the information is redundant, return an empty string. Do not chat."
            )

    async def generate_common_book(
        self, 
        session_id: UUID, 
        transcript_text: str, 
        pdf_text_chunks: List[str],
        mode: IntelligenceMode
    ) -> str:
        """
        Orchestrates the creation of the Unified Study Guide.
        """
        logger.info(f"[{session_id}] Starting Fusion Logic. Base: {len(transcript_text)} chars, Secondary Chunks: {len(pdf_text_chunks)}")

        # Step 1: Establish the Base Layer (The Narrative Skeleton)
        # We assume the video transcript provides the best chronological flow.
        base_layer = transcript_text
        
        # Step 2: Create a summary of the Base Layer to use as the "Context Filter"
        # We can't pass the whole transcript for every comparison (context window limits),
        # so we generate a high-density summary of what we already know.
        base_summary = await self.llm.generate_summary(base_layer, mode)
        logger.info(f"[{session_id}] Base Layer summary generated.")

        # Step 3: Delta Analysis (The "Burner" Loop)
        # We process chunks in parallel batches to speed up the "Set Difference" operation.
        unique_insights = []
        
        batch_size = 5 # Process 5 chunks at a time to respect Rate Limits
        for i in range(0, len(pdf_text_chunks), batch_size):
            batch = pdf_text_chunks[i : i + batch_size]
            tasks = [
                self._extract_unique_delta(chunk, base_summary, mode) 
                for chunk in batch
            ]
            
            # Run batch concurrently
            batch_results = await asyncio.gather(*tasks)
            
            # Filter out empty results (redundant chunks)
            for res in batch_results:
                if res and len(res.strip()) > 10: # Minimum valid length
                    unique_insights.append(res)
            
            logger.debug(f"[{session_id}] Processed batch {i}-{i+batch_size}. Found {len(unique_insights)} unique points so far.")

        # Step 4: Final Synthesis
        # We weave the Base Layer and the Unique Insights into a coherent structure.
        final_manuscript = await self._synthesize_final_narrative(
            base_layer, 
            unique_insights, 
            mode
        )
        
        return final_manuscript

    async def _extract_unique_delta(
        self, 
        chunk: str, 
        known_context: str, 
        mode: IntelligenceMode
    ) -> str:
        """
        Performs the mathematical set difference: Output = Chunk \ Known_Context
        """
        prompt = (
            f"KNOWN CONTEXT (What we already know):\n{known_context}\n\n"
            f"NEW TEXT CHUNK (Analyze this):\n{chunk}\n\n"
            "TASK: Identify ONLY the mathematical formulas, specific definitions, or historical dates "
            "in the 'NEW TEXT' that are NOT mentioned in the 'KNOWN CONTEXT'. "
            "Return them as a bulleted list. If fully redundant, return 'NO_NEW_INFO'."
        )

        try:
            response = await self.llm.generate_text(
                system_prompt=self.system_prompt_template,
                user_prompt=prompt,
                mode=mode,
                temperature=0.1 # Strict logic, no creativity
            )
            
            if "NO_NEW_INFO" in response:
                return ""
            return response
            
        except Exception as e:
            logger.error(f"Delta analysis failed for chunk: {e}")
            return ""

    async def _synthesize_final_narrative(
        self, 
        base_text: str, 
        insights: List[str], 
        mode: IntelligenceMode
    ) -> str:
        """
        Merges the skeleton and the extracted organs into a body.
        """
        secondary_content = "\n".join(insights)
        
        prompt = (
            "You are an expert textbook editor. Create a 'Common Book' study guide.\n"
            "Source 1 (Narrative Flow): Use this for the structure.\n"
            f"{base_text[:15000]}...\n\n" # Truncate if necessary or use RAG if huge
            "Source 2 (Deep Dives/Formulas): Integrate these missing details naturally.\n"
            f"{secondary_content}\n\n"
            "CRITICAL INSTRUCTION: You MUST include video timestamps (e.g., [12:45]) for key definitions, "
            "formulas, and important concepts. The base text contains these timestamps.\n"
            "Output formatted in Markdown with clear headers."
        )
        
        return await self.llm.generate_text(
            system_prompt="You are a specialized academic synthesizer.",
            user_prompt=prompt,
            mode=mode
        )