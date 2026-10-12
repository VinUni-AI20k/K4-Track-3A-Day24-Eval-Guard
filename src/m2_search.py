from __future__ import annotations

"""Vietnamese BM25 + Qdrant dense retrieval with reciprocal-rank fusion."""

from dataclasses import dataclass

from config import (
    BM25_TOP_K,
    COLLECTION_NAME,
    DENSE_TOP_K,
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    HYBRID_TOP_K,
    QDRANT_HOST,
    QDRANT_PORT,
)


@dataclass
class SearchResult:
    text: str
    score: float
    metadata: dict
    method: str


def segment_vietnamese(text: str) -> str:
    try:
        from underthesea import word_tokenize

        return word_tokenize(text, format="text").replace("_", " ")
    except Exception:
        return text


class BM25Search:
    def __init__(self):
        self.documents: list[dict] = []
        self.bm25 = None

    def index(self, chunks: list[dict]) -> None:
        from rank_bm25 import BM25Okapi

        self.documents = list(chunks)
        tokens = [segment_vietnamese(chunk["text"]).lower().split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokens) if tokens else None

    def search(self, query: str, top_k: int = BM25_TOP_K) -> list[SearchResult]:
        if self.bm25 is None or not query.strip():
            return []
        scores = self.bm25.get_scores(segment_vietnamese(query).lower().split())
        indices = sorted(range(len(scores)), key=lambda index: float(scores[index]), reverse=True)[:top_k]
        return [
            SearchResult(self.documents[index]["text"], float(scores[index]),
                         dict(self.documents[index].get("metadata", {})), "bm25")
            for index in indices if float(scores[index]) > 0
        ]


class DenseSearch:
    def __init__(self, client=None):
        if client is None:
            from qdrant_client import QdrantClient

            client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=10)
        self.client = client
        self._encoder = None

    def _get_encoder(self):
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer

            self._encoder = SentenceTransformer(EMBEDDING_MODEL)
        return self._encoder

    def _ensure_collection(self, collection: str, vector_size: int) -> None:
        from qdrant_client.models import Distance, VectorParams

        collections = {item.name for item in self.client.get_collections().collections}
        if collection not in collections:
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            return
        info = self.client.get_collection(collection)
        vectors = info.config.params.vectors
        existing_size = getattr(vectors, "size", None)
        if existing_size != vector_size:
            raise ValueError(
                f"Qdrant collection {collection!r} uses dimension {existing_size}; "
                f"the configured encoder produced {vector_size}. Refusing to reset it automatically."
            )

    def index(self, chunks: list[dict], collection: str = COLLECTION_NAME) -> None:
        """Upsert deterministic points without deleting an existing collection."""
        if not chunks:
            return
        from qdrant_client.models import PointStruct

        vectors = self._get_encoder().encode([chunk["text"] for chunk in chunks], show_progress_bar=True)
        vector_size = len(vectors[0])
        if vector_size != EMBEDDING_DIM:
            raise ValueError(
                f"Embedding model {EMBEDDING_MODEL!r} produced {vector_size} dimensions; "
                f"config.EMBEDDING_DIM is {EMBEDDING_DIM}."
            )
        self._ensure_collection(collection, vector_size)
        points = [
            PointStruct(id=index, vector=vector.tolist(),
                        payload={**chunk.get("metadata", {}), "text": chunk["text"]})
            for index, (chunk, vector) in enumerate(zip(chunks, vectors))
        ]
        self.client.upsert(collection_name=collection, points=points, wait=True)

    def search(self, query: str, top_k: int = DENSE_TOP_K,
               collection: str = COLLECTION_NAME) -> list[SearchResult]:
        if not query.strip():
            return []
        vector = self._get_encoder().encode(query).tolist()
        points = self.client.search(
            collection_name=collection,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
        )
        output: list[SearchResult] = []
        for point in points:
            payload = dict(point.payload or {})
            text = str(payload.pop("text", ""))
            if text.strip():
                output.append(SearchResult(text, float(point.score), payload, "dense"))
        return output


def reciprocal_rank_fusion(
    results_list: list[list[SearchResult]],
    k: int = 60,
    top_k: int = HYBRID_TOP_K,
) -> list[SearchResult]:
    fused: dict[tuple[str, str], dict] = {}
    for results in results_list:
        for rank, result in enumerate(results, start=1):
            key = (str(result.metadata.get("source", "")), result.text)
            entry = fused.setdefault(key, {"score": 0.0, "result": result})
            entry["score"] += 1.0 / (k + rank)
    ranked = sorted(fused.values(), key=lambda item: item["score"], reverse=True)[:top_k]
    return [SearchResult(item["result"].text, float(item["score"]),
                         dict(item["result"].metadata), "hybrid") for item in ranked]


class HybridSearch:
    def __init__(self, dense_client=None):
        self.bm25 = BM25Search()
        self.dense = DenseSearch(client=dense_client)

    def index(self, chunks: list[dict]) -> None:
        self.bm25.index(chunks)
        self.dense.index(chunks)

    def search(self, query: str, top_k: int = HYBRID_TOP_K) -> list[SearchResult]:
        return reciprocal_rank_fusion(
            [self.bm25.search(query, BM25_TOP_K), self.dense.search(query, DENSE_TOP_K)],
            top_k=top_k,
        )
