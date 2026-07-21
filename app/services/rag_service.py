from sqlalchemy.orm import Session
from app.models.vector_model import DocumentChunk
from app.rag.chunking import recursive_character_splitting
from sentence_transformers import SentenceTransformer

# Local lightweight free model load kar rahe hain
model = SentenceTransformer('all-MiniLM-L6-v2')

def add_documents_to_pgvector(db: Session, text: str):
    chunks = recursive_character_splitting(text, chunk_size=500, overlap=50)
    
    for chunk in chunks:
        # Local model se embedding generate hongi (No API key / No Quota issue)
        embedding = model.encode(chunk).tolist()
        
        db_chunk = DocumentChunk(content=chunk, embedding=embedding)
        db.add(db_chunk)
    
    db.commit()
    return {"message": f"Successfully added {len(chunks)} chunks to pgvector!"}

def search_pgvector(db: Session, query: str, top_k: int = 3):
    # Query ke liye bhi local model se embedding banegi
    query_embedding = model.encode(query).tolist()
    
    results = db.query(DocumentChunk).order_by(
        DocumentChunk.embedding.cosine_distance(query_embedding)
    ).limit(top_k).all()
    
    return [r.content for r in results]