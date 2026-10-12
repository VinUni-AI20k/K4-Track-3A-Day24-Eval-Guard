from __future__ import annotations

"""Cross-encoder reranking adapted from the Day 18 pipeline."""

import time
from dataclasses import dataclass

from config import RERANK_TOP_K


@dataclass
class RerankResult:
    text: str
    original_score: float
    rerank_score: float
    metadata: dict
    rank: int


class CrossEncoderReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(self, query: str, documents: list[dict],
               top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        if not documents or top_k <= 0:
            return []
        for document in documents:
            if not isinstance(document.get("text"), str):
                raise TypeError("Each reranker document requires a text string")
        scores = self._load_model().predict([(query, document["text"]) for document in documents])
        if hasattr(scores, "tolist"):
            scores = scores.tolist()
        if isinstance(scores, (int, float)):
            scores = [scores]
        scored = sorted(zip(scores, documents), key=lambda pair: float(pair[0]), reverse=True)
        return [
            RerankResult(
                text=document["text"],
                original_score=float(document.get("score", 0.0)),
                rerank_score=float(score),
                metadata=dict(document.get("metadata", {})),
                rank=rank,
            )
            for rank, (score, document) in enumerate(scored[:top_k], start=1)
        ]


class FlashrankReranker:
    """Optional lightweight alternative, retained for Day 18 API compatibility."""

    def __init__(self):
        self._model = None

    def rerank(self, query: str, documents: list[dict],
               top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        if not documents or top_k <= 0:
            return []
        from flashrank import Ranker, RerankRequest

        if self._model is None:
            self._model = Ranker()
        passages = [{"id": index, "text": document["text"], "meta": document}
                    for index, document in enumerate(documents)]
        ranked = self._model.rerank(RerankRequest(query=query, passages=passages))[:top_k]
        return [
            RerankResult(
                text=item["text"],
                original_score=float(item["meta"].get("score", 0.0)),
                rerank_score=float(item["score"]),
                metadata=dict(item["meta"].get("metadata", {})),
                rank=rank,
            )
            for rank, item in enumerate(ranked, start=1)
        ]


def benchmark_reranker(reranker, query: str, documents: list[dict], n_runs: int = 5) -> dict:
    if n_runs <= 0:
        raise ValueError("n_runs must be positive")
    samples = []
    for _ in range(n_runs):
        started = time.perf_counter()
        reranker.rerank(query, documents)
        samples.append((time.perf_counter() - started) * 1000)
    return {"avg_ms": sum(samples) / len(samples), "min_ms": min(samples), "max_ms": max(samples)}
