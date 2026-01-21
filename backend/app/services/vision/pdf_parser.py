import fitz  # PyMuPDF
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Tuple
from uuid import UUID

from app.services.vision.describer import ImageDescriber

# Setup logger
logger = logging.getLogger(__name__)

class PDFParser:
    """
    Handles the extraction of text and visual data from PDFs.
    
    Workflow:
    1. Iterates through PDF pages.
    2. Extracts raw text.
    3. Detects images -> Saves them -> Sends to Llama-Vision.
    4. Injects the AI-generated description back into the text stream.
    """

    def __init__(self):
        self.vision_model = ImageDescriber()

    async def parse(self, session_id: UUID, file_path: Path, output_dir: Path) -> List[str]:
        """
        Main entry point.
        
        Args:
            session_id: For logging and isolation.
            file_path: Path to the input PDF.
            output_dir: Where to save extracted images for processing.
            
        Returns:
            List[str]: A list of text chunks (roughly one per page) containing 
                       both the original text and the image descriptions.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        doc = fitz.open(file_path)
        logger.info(f"[{session_id}] Parsing PDF: {file_path.name} ({len(doc)} pages)")

        parsed_pages = []
        
        # We collect all image tasks to run them in parallel later if needed,
        # but for order preservation, processing page-by-page is safer.
        
        for page_num, page in enumerate(doc):
            # 1. Extract Text
            text = page.get_text()
            
            # 2. Extract and Process Images on this page
            image_descriptions = await self._process_page_images(
                session_id, 
                page, 
                page_num, 
                output_dir
            )
            
            # 3. Combine
            # We append descriptions at the end of the page text. 
            # (Sophisticated layout analysis to insert exactly where the image was is complex; 
            # appending is sufficient for RAG context).
            full_page_content = f"--- Page {page_num + 1} ---\n{text}\n{image_descriptions}"
            parsed_pages.append(full_page_content)

        return parsed_pages

    async def _process_page_images(
        self, 
        session_id: UUID, 
        page: fitz.Page, 
        page_num: int, 
        output_dir: Path
    ) -> str:
        """
        Extracts images from a single page and gets their descriptions.
        """
        image_list = page.get_images(full=True)
        if not image_list:
            return ""

        descriptions = []
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Filter: Skip tiny images (likely icons, footers, logos)
            if len(image_bytes) < 5 * 1024: # Skip < 5KB
                continue

            # Save image to temp
            image_filename = f"p{page_num}_img{img_index}.{image_ext}"
            image_path = output_dir / image_filename
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            # Call Llama-Vision
            # We await here, but in a highly optimized version, we could gather all these futures.
            desc = await self.vision_model.describe_image(image_path)
            
            if desc and "Description Unavailable" not in desc:
                descriptions.append(f"\n[FIGURE ON PAGE {page_num + 1}]: {desc}\n")

        return "\n".join(descriptions)