import math
from typing import List, Dict, Any

# 1. Similarity Metrics Implementation (Math logic)
def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)

def dot_product_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    # Useful jab vectors normalized hon (jaise OpenAI models ke kuch cases mein)
    return sum(a * b for a, b in zip(vec_a, vec_b))

def euclidean_distance(vec_a: List[float], vec_b: List[float]) -> float:
    # L2 distance: Jitni choti value hogi, vectors utne hi close honge
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))


# 2. Embedding Model Options Configuration Tradeoffs
EMBEDDING_MODEL_OPTIONS: Dict[str, Dict[str, Any]] = {
    "openai_small": {
        "model_name": "text-embedding-3-small",
        "dimensions": 1536,
        "type": "Managed / Cloud API",
        "tradeoff": "Fast, cost-effective, high quality for general purpose."
    },
    "openai_large": {
        "model_name": "text-embedding-3-large",
        "dimensions": 3072,
        "type": "Managed / Cloud API",
        "tradeoff": "Highest accuracy, but higher dimensions mean more storage and slower search."
    },
    "opensource_minilm": {
        "model_name": "all-MiniLM-L6-v2",
        "dimensions": 384,
        "type": "Self-hosted / Local (Sentence-Transformers)",
        "tradeoff": "Lightweight, runs locally for free, smaller dimensions, good for constrained environments."
    }
}

def get_model_info(model_key: str) -> Dict[str, Any]:
    return EMBEDDING_MODEL_OPTIONS.get(model_key, EMBEDDING_MODEL_OPTIONS["openai_small"])