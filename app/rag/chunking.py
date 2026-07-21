import re
from typing import List

# 1. Fixed-Size Chunking (Jo humne pehle use kiya)
def fixed_size_chunking(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# 2. Sentence / Paragraph-based Chunking
def sentence_chunking(text: str, max_chunk_sentences: int = 3) -> List[str]:
    # Sentences mein split karne ke liye regex (periods, exclamation, question marks)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    for i in range(0, len(sentences), max_chunk_sentences):
        chunk = " ".join(sentences[i:i + max_chunk_sentences])
        chunks.append(chunk)
    return chunks

# 3. Recursive Character Splitting (LangChain style logic)
def recursive_character_splitting(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    # Pehle paragraphs par todne ki koshish karein, phir lines, phir spaces par
    separators = ["\n\n", "\n", " ", ""]
    
    def _split(txt, seps):
        if len(txt) <= chunk_size:
            return [txt]
        
        current_sep = seps[0]
        next_seps = seps[1:] if len(seps) > 1 else [""]
        
        splits = txt.split(current_sep)
        result = []
        current_chunk = ""
        
        for part in splits:
            if len(current_chunk) + len(part) + len(current_sep) <= chunk_size:
                current_chunk += (current_sep if current_chunk else "") + part
            else:
                if current_chunk:
                    result.append(current_chunk)
                if len(part) > chunk_size:
                    result.extend(_split(part, next_seps))
                else:
                    current_chunk = part
        if current_chunk:
            result.append(current_chunk)
        return result

    return _split(text, separators)

# 4. Semantic Chunking (Basic Logic)
def semantic_chunking(text: str) -> List[str]:
    # Sentences mein split karein
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if not sentences:
        return [text]
    
    chunks = []
    current_chunk = [sentences[0]]
    
    # Simple semantic rule: Agar sentence lamba ho ya paragraph change ho, toh naya chunk shuru karo
    # (Advanced level par yahan embeddings cosine distance use hota hai)
    for i in range(1, len(sentences)):
        # Yahan hum basic grouping kar rahe hain; production mein sentence embeddings nikal kar distance dekhte hain
        if len(" ".join(current_chunk)) > 400 or len(sentences[i]) > 100:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks