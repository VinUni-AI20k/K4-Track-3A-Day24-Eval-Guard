from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RERANK_TOP_K


@dataclass
class RerankResult:
    text: str
    score: float = 0.0
    metadata: dict = field(default_factory=dict)


class CrossEncoderReranker:
    """Reranker sử dụng FlashRank hoặc CrossEncoder."""

    def __init__(self):
        self.ranker = None
        try:
            from flashrank import Ranker
            self.ranker = Ranker(model_name="ms-marco-TinyBERT-L-2-v2")
        except Exception as e:
            self.ranker = None

    def rerank(self, question: str, docs: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        if not docs:
            return []

        if self.ranker:
            try:
                from flashrank import RerankRequest
                passages = [{"id": i, "text": d["text"], "meta": d.get("metadata", {})} for i, d in enumerate(docs)]
                request = RerankRequest(query=question, passages=passages)
                reranked = self.ranker.rerank(request)
                results = [
                    RerankResult(
                        text=item["text"],
                        score=float(item.get("score", 0.0)),
                        metadata=item.get("meta", {}),
                    )
                    for item in reranked[:top_k]
                ]
                return results
            except Exception:
                pass

        return [
            RerankResult(
                text=d["text"],
                score=float(d.get("score", 0.0)),
                metadata=d.get("metadata", {}),
            )
            for d in docs[:top_k]
        ]
