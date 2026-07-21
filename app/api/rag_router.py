from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db  # Apne database session ka dependency import karein
from app.services.rag_service import add_documents_to_pgvector, search_pgvector

router = APIRouter(prefix="/rag", tags=["RAG Pipeline"])

@router.post("/ingest")
def ingest_document(text: str, db: Session = Depends(get_db)):
    """Documents ko chunk karke pgvector mein store karne ke liye"""
    return add_documents_to_pgvector(db, text)

@router.post("/search")
def search_documents(query: str, top_k: int = 3, db: Session = Depends(get_db)):
    """Query ke mutabiq relevant chunks search karne ke liye"""
    results = search_pgvector(db, query, top_k)
    return {"query": query, "results": results}