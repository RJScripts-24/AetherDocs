import chromadb
from app.core.config import settings
from typing import List

# client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)

def add_documents(collection_name: str, documents: List[str], metadatas: List[dict] = None):
    # collection = client.get_or_create_collection(collection_name)
    # collection.add(
    #     documents=documents,
    #     metadatas=metadatas,
    #     ids=[str(i) for i in range(len(documents))]
    # )
    pass
