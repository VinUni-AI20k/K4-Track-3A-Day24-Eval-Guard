"""Offline contract tests for the integrated Member 1 RAG modules."""

from types import SimpleNamespace

import numpy as np

from src.m1_chunking import chunk_hierarchical
from src.m2_search import BM25Search, DenseSearch, reciprocal_rank_fusion
from src.m3_rerank import CrossEncoderReranker
from src.m4_eval import evaluate_ragas
from src.m5_enrichment import enrich_chunks


def test_hierarchical_chunks_preserve_metadata_and_unique_parent_ids():
    parents_a, children_a = chunk_hierarchical("Alpha sentence.\n\nBeta sentence.", metadata={"source": "a.md"})
    parents_b, children_b = chunk_hierarchical("Alpha sentence.\n\nBeta sentence.", metadata={"source": "b.md"})
    assert parents_a and children_a
    assert {child.parent_id for child in children_a} <= {parent.parent_id for parent in parents_a}
    assert {parent.parent_id for parent in parents_a}.isdisjoint({parent.parent_id for parent in parents_b})
    assert all(child.metadata["source"] == "a.md" for child in children_a)


def test_bm25_and_rrf_return_contract_objects():
    chunks = [
        {"text": "Nhân viên nghỉ phép mười hai ngày", "metadata": {"source": "leave.md"}},
        {"text": "Mật khẩu thay đổi định kỳ", "metadata": {"source": "password.md"}},
        {"text": "Quy trình thanh toán công tác phí", "metadata": {"source": "expense.md"}},
    ]
    bm25 = BM25Search()
    bm25.index(chunks)
    results = bm25.search("nghỉ phép")
    fused = reciprocal_rank_fusion([results, results])
    assert fused and fused[0].method == "hybrid"
    assert fused[0].metadata["source"] == "leave.md"


class _FakeEncoder:
    def encode(self, texts, show_progress_bar=False):
        if isinstance(texts, str):
            return np.ones(1024)
        return np.ones((len(texts), 1024))


class _FakeQdrant:
    def __init__(self):
        self.created = False
        self.upserted = []

    def get_collections(self):
        return SimpleNamespace(collections=[])

    def create_collection(self, **kwargs):
        self.created = True

    def upsert(self, **kwargs):
        self.upserted = kwargs["points"]

    def search(self, **kwargs):
        return [SimpleNamespace(score=0.75, payload={"text": "context", "source": "policy.md"})]


def test_dense_search_uses_installed_client_api_and_preserves_payload():
    client = _FakeQdrant()
    dense = DenseSearch(client=client)
    dense._encoder = _FakeEncoder()
    dense.index([{"text": "context", "metadata": {"source": "policy.md"}}])
    result = dense.search("question")
    assert client.created and len(client.upserted) == 1
    assert result[0].text == "context" and result[0].metadata == {"source": "policy.md"}


def test_reranker_returns_sorted_metadata():
    reranker = CrossEncoderReranker()
    reranker._model = SimpleNamespace(predict=lambda pairs: np.array([0.1, 0.9]))
    rows = reranker.rerank("q", [
        {"text": "low", "score": 0.2, "metadata": {"id": 1}},
        {"text": "high", "score": 0.3, "metadata": {"id": 2}},
    ], top_k=1)
    assert rows[0].text == "high" and rows[0].metadata == {"id": 2}


def test_offline_enrichment_preserves_count_order_and_metadata():
    chunks = [
        {"text": "First policy sentence.", "metadata": {"source": "one.md", "parent_id": "p1"}},
        {"text": "Second policy sentence.", "metadata": {"source": "two.md", "parent_id": "p2"}},
    ]
    rows = enrich_chunks(chunks, use_api=False)
    assert [row.original_text for row in rows] == [chunk["text"] for chunk in chunks]
    assert [row.auto_metadata["parent_id"] for row in rows] == ["p1", "p2"]
    assert all(row.enriched_text.strip() for row in rows)


def test_empty_ragas_result_has_required_provenance():
    result = evaluate_ragas([], [], [], [])
    assert result["per_question"] == []
    assert result["metadata"]["evaluator_models"]
