import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.schemas.chat import ChatRequest, ChatResponse, Citation
from app.services.vector.db import VectorDBClient
from app.services.synthesis.generator import LLMClient
from app.schemas.ingestion import IntelligenceMode

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/query", response_model=ChatResponse)
async def query_chat(request: ChatRequest):
    """
    RAG Endpoint:
    1. Retrieve relevant chunks from ChromaDB.
    2. Construct prompt with context.
    3. Generate answer via Llama-3.
    """
    session_id = request.session_id
    query_text = request.query
    
    try:
        # 1. Retrieval
        vector_db = VectorDBClient()
        # Retrieve top 5 chunks
        results = vector_db.query(session_id, query_text, n_results=8)
        
        if not results:
            return ChatResponse(
                answer="I couldn't find any documents in this session. Please upload a file or video first.",
                citations=[]
            )

        # 2. Context Construction
        # We build citation labels EXCLUSIVELY from chunk metadata (not from text content).
        # This ensures page numbers are always accurate regardless of how text was chunked.
        context_str = ""
        citations = []
        
        for idx, res in enumerate(results):
            meta = res.get("metadata", {})
            source = meta.get("source", "Unknown")
            timestamp = meta.get("timestamp") # "12:45"
            page = meta.get("page")
            
            # Build citation label from metadata only
            if timestamp:
                citation_label = f"[Video {timestamp}]"
            elif page:
                citation_label = f"[Source: {source}, Page {page}]"
            else:
                citation_label = f"[Source: {source}]"

            # Format context string with metadata-derived label
            context_str += f"{citation_label}: {res['text']}\n\n"
            
            # Build citation object
            citations.append(Citation(
                source_file=source,
                page_number=page,
                timestamp=timestamp, 
                snippet=res['text'][:100] + "...",
                score=res.get("score", 0.0)
            ))

        # 3. Generation
        llm = LLMClient()
        
        system_prompt = (
            "You are AetherDocs, an ephemeral study assistant. "
            "Answer the user's question based on the provided context. "
            "If the context contains information relevant to the question, even partially, provide a helpful answer. "
            "Only say 'I cannot answer this based on the provided materials' if the context is completely unrelated to the question. "
            "Each piece of context is prefixed with a citation tag like [Source: filename, Page N] or [Video MM:SS]. "
            "You MUST cite your sources using ONLY these exact citation tags as provided. "
            "NEVER infer, guess, or fabricate page numbers or timestamps. "
            "When the user asks 'on which page' or 'where can I find', always reference the citation tags from the relevant context blocks. "
            "Only use the citation tags that appear at the start of each context block."
        )
        
        user_prompt = (
            f"CONTEXT:\n{context_str}\n\n"
            f"USER QUESTION: {query_text}\n\n"
            f"INSTRUCTIONS: Answer the question using the context above. "
            f"If the user asks about a location (page number, timestamp), reference the citation tags from the context blocks that contain the relevant information."
        )

        answer = await llm.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            mode=IntelligenceMode.FAST # Chat usually implies speed
        )
        
        return ChatResponse(
            answer=answer,
            citations=citations
        )

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/locator")
async def locator_mode(request: ChatRequest):
    """
    Scans the vector database for all chronological mentions of a topic.
    Returns a sorted list of timestamps/pages.
    """
    session_id = request.session_id
    query_text = request.query
    
    try:
        vector_db = VectorDBClient()
        # Fetch more results for a broad "Scan"
        results = vector_db.query(session_id, query_text, n_results=50)
        
        locations = []
        for res in results:
            meta = res.get("metadata", {})
            loc = {
                "source": meta.get("source", "Unknown"),
                "snippet": res["text"][:150] + "...",
                "score": res.get("score", 0),
                "timestamp": meta.get("timestamp"),
                "start_seconds": meta.get("start_seconds", 0),
                "page": meta.get("page", 0)
            }
            locations.append(loc)
            
        # Sort chronologically: Video First (by seconds), then PDF (by page)
        # This is a heuristic sort
        def sort_key(x):
            weight = 0 if x["source"] == "video" else 100000
            val = x["start_seconds"] if x["source"] == "video" else x["page"]
            return weight + (val or 0)
            
        locations.sort(key=sort_key)
        
        return {"mentions": locations}
        
    except Exception as e:
        logger.error(f"Locator failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
