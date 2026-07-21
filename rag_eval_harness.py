import time
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class EvalConfig:
    chunking_strategy: str  # "fixed-size" vs "semantic"
    chunk_size: int
    chunk_overlap: int
    top_k: int
    use_reranker: bool
    use_hybrid: bool

@dataclass
class EvalResult:
    config: EvalConfig
    question: str
    retrieved_chunks: List[str]
    retrieved_order: List[int]
    final_answer: str
    hit_rate_score: float  # 1.0 agar relevant chunk mila, 0.0 agar nahi
    latency_ms: float

class RAGEvaluationHarness:
    def __init__(self, eval_dataset: List[Dict[str, Any]]):
        self.eval_dataset = eval_dataset
        self.results: List[EvalResult] = []

    def mock_retrieve_and_generate(self, question: str, config: EvalConfig) -> Dict[str, Any]:
        """
        Yahan aap apni actual RAG pipeline call karein gi jo database/vector store 
        se chunks retrieve kar ke LLM response aur chunks list degi.
        """
        start_time = time.time()
        
        # Simulated retrieval behavior based on configuration parameters
        chunks = [
            f"Chunk A (Size: {config.chunk_size}, Strategy: {config.chunking_strategy})",
            f"Chunk B (Top K index: {config.top_k}, Re-rank: {config.use_reranker})",
            f"Chunk C (Hybrid Search: {config.use_hybrid})"
        ]
        
        # Agar top_k 1 ho toh chunks kam ho jayenge
        active_chunks = chunks[:config.top_k]
        
        # Simulated final answer generation
        answer = f"Answer generated using {config.chunking_strategy} chunks with top_k={config.top_k} and reranker={config.use_reranker}."
        
        # Simulated Hit-rate metric logic (1.0 if optimal configuration parameters are met)
        hit_score = 1.0 if config.use_reranker and config.use_hybrid else 0.5

        latency = (time.time() - start_time) * 1000

        return {
            "retrieved_chunks": active_chunks,
            "retrieved_order": list(range(len(active_chunks))),
            "final_answer": answer,
            "hit_rate_score": hit_score,
            "latency_ms": latency
        }

    def run_evaluation(self, configs: List[EvalConfig]):
        for config in configs:
            for item in self.eval_dataset:
                question = item["question"]
                res = self.mock_retrieve_and_generate(question, config)
                
                result = EvalResult(
                    config=config,
                    question=question,
                    retrieved_chunks=res["retrieved_chunks"],
                    retrieved_order=res["retrieved_order"],
                    final_answer=res["final_answer"],
                    hit_rate_score=res["hit_rate_score"],
                    latency_ms=res["latency_ms"]
                )
                self.results.append(result)

    def generate_comparison_table(self) -> str:
        """
        Deliverable: Comparison log or table showing how variables changed 
        retrieved chunks, final answers, and hit-rate scores.
        """
        report = []
        report.append("--- RAG RETRIEVAL CONFIGURATION EVALUATION REPORT ---")
        report.append(f"{'Strategy':<15} | {'Size':<6} | {'TopK':<5} | {'Rerank':<7} | {'Hybrid':<7} | {'Hit-Rate':<9} | {'Latency':<8}")
        report.append("-" * 75)
        
        for r in self.results:
            cfg = r.config
            report.append(
                f"{cfg.chunking_strategy:<15} | "
                f"{cfg.chunk_size:<6} | "
                f"{cfg.top_k:<5} | "
                f"{str(cfg.use_reranker):<7} | "
                f"{str(cfg.use_hybrid):<7} | "
                f"{r.hit_rate_score:<9.1f} | "
                f"{r.latency_ms:<6.1f}ms"
            )
        return "\n".join(report)

# --- EXECUTION EXAMPLE ---
if __name__ == "__main__":
    # Eval set questions
    eval_set = [
        {"question": "How do I borrow a book from the library database?"},
        {"question": "What are the rules for maximum book borrowing limits?"}
    ]

    # Test configurations vary karne ke liye
    test_configs = [
        EvalConfig(chunking_strategy="fixed-size", chunk_size=500, chunk_overlap=50, top_k=2, use_reranker=False, use_hybrid=False),
        EvalConfig(chunking_strategy="semantic", chunk_size=400, chunk_overlap=0, top_k=3, use_reranker=True, use_hybrid=True),
    ]

    harness = RAGEvaluationHarness(eval_set)
    harness.run_evaluation(test_configs)
    
    print(harness.generate_comparison_table())