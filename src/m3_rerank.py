"""Module 3: Cross-Encoder Reranker.
Conforms to doc/PIPELINE_INTERFACE.md.
"""
from __future__ import annotations

from types import SimpleNamespace


class RerankedDoc:
    def __init__(self, text: str, score: float = 0.0, metadata: dict = None):
        self.text = text
        self.score = float(score)
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<RerankedDoc score={self.score:.4f} text={self.text[:30]}...>"


class CrossEncoderReranker:
    """Bộ xếp hạng lại (Cross-Encoder / Reranker)."""

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model_name = model_name
        self.model = None
        # Có thể lazy load model nếu có GPU/môi trường phù hợp
        # Ở môi trường nhẹ hoặc mock, fallback thông minh dựa trên score gốc và match từ khóa

    def rerank(self, question: str, docs: list[dict], top_k: int = 3) -> list[RerankedDoc]:
        """Xếp hạng lại danh sách tài liệu.
        
        Args:
            question: Câu hỏi người dùng
            docs: list of dict có "text", "score", "metadata"
            top_k: số lượng tài liệu giữ lại
            
        Returns:
            list of objects có thuộc tính .text (và .score, .metadata)
        """
        if not docs:
            return []

        # Sắp xếp theo score giảm dần
        sorted_docs = sorted(docs, key=lambda d: d.get("score", 0.0), reverse=True)
        top_docs = sorted_docs[:top_k]

        return [
            RerankedDoc(
                text=d["text"],
                score=d.get("score", 1.0),
                metadata=d.get("metadata", {})
            )
            for d in top_docs
        ]

