from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text

# 1. Advanced Recursive Chunking
def get_chunks(text_content: str, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text_content)

# 2. Embedding & Vector Logic
# Hum OpenAI ka model use kar rahe hain, aap yahan sentence-transformers bhi daal sakti hain
def generate_embeddings(text: str):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return embeddings.embed_query(text)

# 3. Vector Similarity (Postgres pgvector optimized)
def search_similar_chunks(db, query_vector, table_name="book_chunks", limit=3):
    # HNSW ya IVFFlat index ka use karte hue optimized query
    # <-> operator Postgres mein Cosine Distance nikalta hai
    query = text(f"""
        SELECT content FROM {table_name} 
        ORDER BY embedding <-> :vector 
        LIMIT :limit
    """)
    result = db.execute(query, {"vector": str(query_vector), "limit": limit})
    return [row[0] for row in result]