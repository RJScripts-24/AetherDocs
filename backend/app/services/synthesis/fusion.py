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
    
    Optimized for Groq free-tier (6000 TPM limit):
    - Small, focused prompts
    - Sequential processing with delays
    - Direct content concatenation instead of LLM re-summarization
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        
        try:
            with open("app/templates/prompts/deduplication.txt", "r") as f:
                self.system_prompt_template = f.read()
        except FileNotFoundError:
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
        mode: IntelligenceMode,
        image_descriptions: List[str] = None
    ) -> str:
        """
        Orchestrates the creation of the Unified Study Guide.
        Optimized for Groq free-tier TPM limits.
        """
        logger.info(f"[{session_id}] Starting Fusion Logic. Base: {len(transcript_text)} chars, Secondary Chunks: {len(pdf_text_chunks)}, Images: {len(image_descriptions or [])}")

        # Step 1: Base Layer
        base_layer = transcript_text
        
        # Step 2: Generate a SHORT summary of base layer for delta comparison
        # Keep it brief to save tokens
        base_summary = await self.llm.generate_summary(base_layer, mode)
        logger.info(f"[{session_id}] Base Layer summary generated ({len(base_summary)} chars).")
        
        await asyncio.sleep(3)  # Wait for TPM to reset

        # Step 3: Delta Analysis — process ONE chunk at a time (safest for free tier)
        unique_insights = []
        
        for i, chunk in enumerate(pdf_text_chunks):
            logger.info(f"[{session_id}] Delta analysis chunk {i+1}/{len(pdf_text_chunks)} ({len(chunk)} chars)...")
            
            delta = await self._extract_unique_delta(chunk, base_summary, mode)
            
            if delta and len(delta.strip()) > 10:
                unique_insights.append(delta)
                logger.info(f"[{session_id}]   → Found unique content ({len(delta)} chars)")
            else:
                logger.info(f"[{session_id}]   → Redundant (skipped)")
            
            # Wait between EVERY call to stay under 6000 TPM
            await asyncio.sleep(4)

        logger.info(f"[{session_id}] Delta analysis complete. {len(unique_insights)} unique insights from {len(pdf_text_chunks)} chunks.")

        # Step 4: Build final document by DIRECTLY combining content
        # Instead of asking LLM to re-synthesize everything (which exceeds TPM),
        # we build the document structure ourselves and only use LLM for the intro/conclusion
        final_manuscript = await self._build_final_document(
            session_id,
            base_layer, 
            unique_insights, 
            mode,
            image_descriptions=image_descriptions or []
        )
        
        logger.info(f"[{session_id}] Final manuscript: {len(final_manuscript)} chars")
        return final_manuscript

    async def _extract_unique_delta(
        self, 
        chunk: str, 
        known_context: str, 
        mode: IntelligenceMode
    ) -> str:
        """
        Performs set difference: Output = Chunk \ Known_Context
        Uses trimmed prompts to fit within TPM limits.
        """
        # Keep both inputs short to fit in ~1500 tokens input
        trimmed_context = known_context[:2000]
        trimmed_chunk = chunk[:2000]
        
        prompt = (
            f"KNOWN CONTEXT:\n{trimmed_context}\n\n"
            f"NEW TEXT:\n{trimmed_chunk}\n\n"
            "TASK: List ALL unique information from 'NEW TEXT' not in 'KNOWN CONTEXT'. "
            "Include: facts, definitions, formulas, descriptions, technical details, names, processes. "
            "Return as a bulleted list. If fully redundant, return 'NO_NEW_INFO'."
        )

        try:
            response = await self.llm.generate_text(
                system_prompt=self.system_prompt_template,
                user_prompt=prompt,
                mode=mode,
                temperature=0.1,
                max_tokens=1500
            )
            
            if "NO_NEW_INFO" in response:
                return ""
            return response
            
        except Exception as e:
            logger.error(f"Delta analysis failed for chunk: {e}")
            return ""

    async def _build_final_document(
        self,
        session_id: UUID,
        base_text: str, 
        insights: List[str], 
        mode: IntelligenceMode,
        image_descriptions: List[str] = None
    ) -> str:
        """
        Builds the final document by combining content with minimal LLM usage.
        Uses LLM only for intro/conclusion, concatenates the rest directly.
        This avoids exceeding TPM limits.
        """
        logger.info(f"[{session_id}] Building final document: {len(insights)} insights, {len(image_descriptions)} images")
        
        # Part 1: Generate a brief intro using LLM (small prompt)
        intro_prompt = (
            f"Based on this content summary, write a brief 3-4 sentence introduction for a study guide:\n"
            f"{base_text[:1500]}\n\n"
            "Start with '# Common Book — Unified Study Guide' as the title."
        )
        
        intro = await self.llm.generate_text(
            system_prompt="You are a textbook editor. Write a brief introduction.",
            user_prompt=intro_prompt,
            mode=mode,
            max_tokens=500
        )
        
        await asyncio.sleep(4)
        
        # Part 2: Summarize the base transcript using LLM
        base_prompt = (
            "Rewrite the following transcript into a clean, well-organized study section. "
            "Use ## headers for subtopics. Preserve all key information and timestamps.\n\n"
            f"{base_text[:3500]}"
        )
        
        base_section = await self.llm.generate_text(
            system_prompt="You are a textbook editor creating a study guide section.",
            user_prompt=base_prompt,
            mode=mode,
            max_tokens=2000
        )
        
        await asyncio.sleep(4)
        
        # Part 3: Format insights from documents (combine them directly, no LLM needed)
        insights_section = ""
        if insights:
            insights_section = "\n\n# Document Insights & Key Points\n\n"
            insights_section += "The following unique insights were extracted from the uploaded documents:\n\n"
            for i, insight in enumerate(insights):
                insights_section += f"## Key Points — Set {i+1}\n\n{insight}\n\n"
        
        # Part 4: Add image descriptions directly (no LLM needed — already described)
        image_section = ""
        if image_descriptions:
            image_section = "\n\n# Visual Analysis\n\n"
            image_section += "The following visual data was extracted from uploaded images and diagrams:\n\n"
            for desc in image_descriptions:
                image_section += f"{desc}\n\n"
        
        # Part 5: Generate brief conclusion using LLM
        conclusion_prompt = (
            "Write a brief 2-3 sentence conclusion for a study guide that covered these topics:\n"
            f"- Base content: {base_text[:500]}\n"
            f"- {len(insights)} sets of document insights\n"
            f"- {len(image_descriptions)} image analyses\n"
            "Start with '# Conclusion'"
        )
        
        conclusion = await self.llm.generate_text(
            system_prompt="You are a textbook editor. Write a brief conclusion.",
            user_prompt=conclusion_prompt,
            mode=mode,
            max_tokens=500
        )
        
        # Combine all parts
        final_doc = "\n\n".join(filter(None, [
            intro,
            "# Primary Source Content\n",
            base_section,
            insights_section,
            image_section,
            conclusion
        ]))
        
        logger.info(f"[{session_id}] Final document assembled: {len(final_doc)} chars "
                    f"(intro={len(intro)}, base={len(base_section)}, "
                    f"insights={len(insights_section)}, images={len(image_section)}, "
                    f"conclusion={len(conclusion)})")
        
        return final_doc