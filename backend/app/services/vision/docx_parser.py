import logging
from pathlib import Path
from typing import List
from uuid import UUID
import docx

logger = logging.getLogger(__name__)

class DocxParser:
    """
    Handles extraction of text from DOCX files.
    """

    async def parse(self, session_id: UUID, file_path: Path, output_dir: Path) -> List[str]:
        """
        Parses a DOCX file and returns a list of text chunks (one per paragraph or section).
        For now, we group by reasonable chunks or just return the whole text as one large chunk 
        if it's not too big, but pagination is better for RAG.
        
        Since DOCX doesn't have fixed pages like PDF, we chunk by paragraphs (~500 words).
        """
        if not file_path.exists():
            raise FileNotFoundError(f"DOCX not found: {file_path}")

        logger.info(f"[{session_id}] Parsing DOCX: {file_path.name}")
        
        try:
            doc = docx.Document(file_path)
            full_text = []
            
            # Simple extraction: iterate paragraphs
            current_chunk = []
            current_length = 0
            chunks = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                    
                current_chunk.append(text)
                current_length += len(text)
                
                # Approximate 1 page of text (~3000 chars)
                if current_length > 3000:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0
            
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                
            return chunks

        except Exception as e:
            logger.error(f"[{session_id}] DOCX Parse error: {e}")
            raise RuntimeError(f"Failed to parse DOCX: {e}")
