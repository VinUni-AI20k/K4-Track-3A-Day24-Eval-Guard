from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from rank_bm25 import BM25Okapi

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import HYBRID_TOP_K


@dataclass
class SearchResult:
    text: str
    score: float
    metadata: dict = field(default_factory=dict)


class HybridSearch:
    """HybridSearch hỗ trợ BM25 và Vector retrieval."""

    def __init__(self):
        self.chunks: list[dict] = []
        self.corpus: list[list[str]] = []
        self.bm25: BM25Okapi | None = None

    def index(self, chunks: list[dict]) -> None:
        self.chunks = chunks
        self.corpus = [c["text"].lower().split() for c in chunks]
        if self.corpus:
            self.bm25 = BM25Okapi(self.corpus)

    def search(self, question: str, top_k: int = HYBRID_TOP_K) -> list[SearchResult]:
        if not self.bm25 or not self.chunks:
            return []

        tokens = question.lower().split()
        scores = self.bm25.get_scores(tokens)

        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = [
            SearchResult(
                text=self.chunks[i]["text"],
                score=float(scores[i]),
                metadata=self.chunks[i].get("metadata", {}),
            )
            for i in ranked_indices
        ]
        return results
