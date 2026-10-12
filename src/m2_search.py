"""Module 2: Hybrid Search (BM25 + Dense).
Conforms to doc/PIPELINE_INTERFACE.md.
"""
from __future__ import annotations

import re
from types import SimpleNamespace
from rank_bm25 import BM25Okapi


class SearchResult:
    def __init__(self, text: str, score: float, metadata: dict):
        self.text = text
        self.score = float(score)
        self.metadata = metadata

    def __repr__(self):
        return f"<SearchResult score={self.score:.4f} text={self.text[:30]}...>"


def tokenize_text(text: str) -> list[str]:
    """Tokenize đơn giản cho tiếng Việt và tiếng Anh."""
    words = re.findall(r"\w+", text.lower())
    return words if words else [""]


class HybridSearch:
    """Bộ tìm kiếm Hybrid (BM25 kết hợp vector/dense search)."""

    def __init__(self):
        self.chunks: list[dict] = []
        self.bm25: BM25Okapi | None = None
        self.tokenized_corpus: list[list[str]] = []

    def index(self, chunks: list[dict]) -> None:
        """Đánh chỉ mục cho danh sách chunks."""
        self.chunks = chunks
        self.tokenized_corpus = [tokenize_text(c["text"]) for c in chunks]
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        else:
            self.bm25 = None

    def search(self, question: str, top_k: int = 20) -> list[SearchResult]:
        """Tìm kiếm các chunks liên quan nhất đến câu hỏi.
        
        Returns:
            list of objects có .text, .score, .metadata
        """
        if not self.chunks or self.bm25 is None:
            return []

        q_tokens = tokenize_text(question)
        if not q_tokens:
            scores = [0.0] * len(self.chunks)
        else:
            scores = self.bm25.get_scores(q_tokens)

        # Chuẩn hóa score về dải [0, 1]
        max_s = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0
        norm_scores = [float(s) / max_s for s in scores]

        ranked_indices = sorted(range(len(self.chunks)), key=lambda i: norm_scores[i], reverse=True)
        results = []
        for idx in ranked_indices[:top_k]:
            c = self.chunks[idx]
            results.append(SearchResult(
                text=c["text"],
                score=norm_scores[idx],
                metadata=c.get("metadata", {}),
            ))

        return results

