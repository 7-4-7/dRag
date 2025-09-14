from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.rag.pipeline import RAGPipeline
from pathlib import Path

router = APIRouter(prefix="/rag", tags=["rag"])

kb_dir = Path('backend/rag/kb')

class QueryRequest(BaseModel):
    query: str
    web_search: bool

@router.post("/generate_answer")
def generate_answer(body: QueryRequest):
    try:
        rag = RAGPipeline(web_search=body.web_search)
        all_content = rag.load_documents(kb_dir)
        chunks = rag.chunk_text(all_content, chunk_size=500, chunk_overlap=50)
        emb_chunks = rag.embed_chunks(chunks)
        rag.store_embeds(emb_chunks)

        q_emb = rag.query_embed(body.query)
        local_context = rag.lookup_and_retrieval(q_emb=q_emb.tolist(), top_k=3)

        if body.web_search:
            full_context = rag.web_search_needed(query=body.query, context=local_context)
        else:
            full_context = local_context

        result = rag.generate_answer(query=body.query, context=full_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
