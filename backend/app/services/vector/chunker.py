import logging
from typing import List, Dict, Optional
from uuid import UUID

# We use LangChain's logic but implement it standalone to keep dependencies minimal
# or assume langchain-text-splitters is installed. 
# For a raw python implementation without heavy deps, this standard logic works best:

class SemanticChunker:
    """
    Splits long text documents into smaller, semantically coherent chunks.
    Essential for RAG (Retrieval Augmented Generation) to function correctly.
    """

    def __init__(
        self, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ):
        """
        Args:
            chunk_size: Target size of each text block (in characters).
            chunk_overlap: Amount of text to repeat between chunks to preserve context at boundaries.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Priority list of separators to keep text semantically grouped
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text: str, source_metadata: Dict) -> List[Dict]:
        """
        Main entry point. Splits text and attaches metadata to each chunk.
        
        Args:
            text: The full document text.
            source_metadata: Dict containing {'source': 'video.mp4', 'page': 1, 'timestamp': 120}
            
        Returns:
            List of dicts ready for ChromaDB insertion.
        """
        if not text:
            return []

        chunks = self._recursive_split(text)
        
        structured_chunks = []
        for i, chunk_content in enumerate(chunks):
            # Create a rich chunk object
            chunk_obj = {
                "id": f"{source_metadata.get('source_id', 'unknown')}_{i}",
                "text": chunk_content,
                "metadata": {
                    **source_metadata,
                    "chunk_index": i
                }
            }
            structured_chunks.append(chunk_obj)
            
        return structured_chunks

    def _recursive_split(self, text: str) -> List[str]:
        """
        Internal logic to split text based on the separator hierarchy.
        """
        final_chunks = []
        if len(text) <= self.chunk_size:
            return [text]

        # Find the best separator that exists in the text
        separator = ""
        for sep in self.separators:
            if sep in text:
                separator = sep
                break
        
        # If no separator found (one giant word?), fallback to character split
        if separator == "":
            return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]

        # Split using the chosen separator
        splits = text.split(separator)
        
        # Merge splits back together until they reach chunk_size
        current_doc = []
        current_len = 0
        
        for split in splits:
            # If the separator was stripped, we might want to add it back for context depending on logic
            # Here we act simple.
            len_split = len(split)
            
            if current_len + len_split + len(separator) > self.chunk_size:
                if current_len > 0:
                    doc_text = separator.join(current_doc)
                    final_chunks.append(doc_text)
                    
                    # Handle overlap: Keep the last few segments of the previous chunk
                    # This is a simplified overlap logic
                    while current_len > self.chunk_overlap and current_doc:
                        popped = current_doc.pop(0)
                        current_len -= len(popped) + len(separator)
                
                current_doc = [split]
                current_len = len_split
            else:
                current_doc.append(split)
                current_len += len_split + len(separator)
        
        if current_doc:
            final_chunks.append(separator.join(current_doc))
            
        return final_chunks