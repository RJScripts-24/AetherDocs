import logging
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional, Any
from uuid import UUID

from app.core.config import settings

# Setup logger
logger = logging.getLogger(__name__)

class VectorDBClient:
    """
    Manages interactions with the Chroma Vector Store.
    
    Architecture:
    - Uses a separate Collection for each Session UUID.
    - This guarantees strict data isolation (User A cannot search User B's notes).
    - Supports the 'Burner' model by allowing O(1) deletion of the entire collection.
    """

    def __init__(self):
        # Connect to the Chroma container defined in docker-compose
        # host="chromadb", port=8000
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )
        
        # We use a local embedding model to keep data private and free.
        # This runs inside the container (cpu/gpu).
        # "all-MiniLM-L6-v2" is standard for RAG.
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

    def get_or_create_collection(self, session_id: UUID):
        """
        Retrieves the isolated collection for a specific user session.
        """
        collection_name = f"session_{str(session_id)}"
        try:
            return self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"} # Cosine similarity for semantic search
            )
        except Exception as e:
            logger.error(f"Failed to create collection for {session_id}: {e}")
            raise RuntimeError("Vector Store initialization failed.")

    def add_documents(self, session_id: UUID, chunks: List[Dict[str, Any]]):
        """
        Ingests text chunks into the vector store.
        
        Args:
            session_id: The session owner.
            chunks: List of dicts produced by the Chunker service.
                   [{'id': '...', 'text': '...', 'metadata': {...}}]
        """
        if not chunks:
            return

        collection = self.get_or_create_collection(session_id)
        
        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        try:
            # Chroma automatically computes embeddings using the embedding_fn defined in __init__
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"[{session_id}] Indexed {len(chunks)} chunks into ChromaDB.")
        except Exception as e:
            logger.error(f"[{session_id}] Failed to index documents: {e}")
            raise RuntimeError(f"Indexing failed: {e}")

    def query(
        self, 
        session_id: UUID, 
        query_text: str, 
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Performs a Semantic Search (RAG Retrieval).
        """
        try:
            # We don't use get_or_create here; if it doesn't exist, we should probably fail or return empty
            try:
                collection = self.client.get_collection(
                    name=f"session_{str(session_id)}",
                    embedding_function=self.embedding_fn
                )
            except ValueError:
                logger.warning(f"[{session_id}] Query attempted on non-existent collection.")
                return []

            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )

            # Chroma returns a column-oriented dictionary (list of lists). 
            # We convert it to a cleaner list of dicts for the application layer.
            structured_results = []
            
            # Check if we got any results (results['ids'] is a list of lists)
            if results['ids']:
                for i in range(len(results['ids'][0])):
                    item = {
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        # distance is standard, we convert to "relevance score" (1 - distance) approx
                        "score": 1 - results['distances'][0][i] if results['distances'] else 0
                    }
                    structured_results.append(item)

            return structured_results

        except Exception as e:
            logger.error(f"[{session_id}] Vector search failed: {e}")
            return []

    def delete_session_collection(self, session_id: UUID) -> bool:
        """
        The 'Burner' Flush.
        Deletes the entire collection for the session.
        """
        collection_name = f"session_{str(session_id)}"
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"[{session_id}] Vector collection deleted.")
            return True
        except ValueError:
            # Collection didn't exist, technically a success
            return True
        except Exception as e:
            logger.error(f"[{session_id}] Failed to delete vector collection: {e}")
            return False