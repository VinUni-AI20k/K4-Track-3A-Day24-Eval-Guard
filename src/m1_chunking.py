from __future__ import annotations

"""Document loading and chunking adapted from the Day 18 RAG project."""

import glob
import hashlib
import os
import re
from dataclasses import dataclass, field

from config import (
    DATA_DIR,
    HIERARCHICAL_CHILD_SIZE,
    HIERARCHICAL_PARENT_SIZE,
    SEMANTIC_THRESHOLD,
)


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    parent_id: str | None = None


def _extract_pdf_text(path: str) -> str:
    from pypdf import PdfReader

    return "\n\n".join(page.extract_text() or "" for page in PdfReader(path).pages).strip()


def load_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """Load Markdown and text-layer PDFs with stable source metadata."""
    documents: list[dict] = []
    for path in sorted(glob.glob(os.path.join(data_dir, "*.md"))):
        with open(path, encoding="utf-8") as handle:
            text = handle.read().strip()
        if text:
            documents.append({"text": text, "metadata": {"source": os.path.basename(path)}})
    for path in sorted(glob.glob(os.path.join(data_dir, "*.pdf"))):
        text = _extract_pdf_text(path)
        if text:
            documents.append({"text": text, "metadata": {"source": os.path.basename(path)}})
        else:
            print(f"  Warning: skipped {os.path.basename(path)} (no PDF text layer).")
    return documents


def chunk_basic(text: str, chunk_size: int = 500, metadata: dict | None = None) -> list[Chunk]:
    metadata = dict(metadata or {})
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    output: list[Chunk] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if current and len(candidate) > chunk_size:
            output.append(Chunk(current, {**metadata, "chunk_index": len(output)}))
            current = paragraph
        else:
            current = candidate
    if current:
        output.append(Chunk(current, {**metadata, "chunk_index": len(output)}))
    return output


def chunk_semantic(
    text: str,
    threshold: float = SEMANTIC_THRESHOLD,
    metadata: dict | None = None,
) -> list[Chunk]:
    """Group adjacent sentences while their embedding cosine similarity is high."""
    import numpy as np
    from sentence_transformers import SentenceTransformer

    metadata = dict(metadata or {})
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n\n+", text) if s.strip()]
    if len(sentences) < 2:
        return [Chunk(sentences[0], {**metadata, "strategy": "semantic", "chunk_index": 0})] if sentences else []
    embeddings = SentenceTransformer("all-MiniLM-L6-v2").encode(sentences)
    groups = [[sentences[0]]]
    for index in range(1, len(sentences)):
        left, right = embeddings[index - 1], embeddings[index]
        denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
        similarity = float(np.dot(left, right) / denominator) if denominator else 0.0
        (groups.append([sentences[index]]) if similarity < threshold else groups[-1].append(sentences[index]))
    return [
        Chunk(" ".join(group), {**metadata, "strategy": "semantic", "chunk_index": index})
        for index, group in enumerate(groups)
    ]


def _split_oversize(text: str, size: int) -> list[str]:
    return [text[start : start + size].strip() for start in range(0, len(text), size) if text[start : start + size].strip()]


def chunk_hierarchical(
    text: str,
    parent_size: int = HIERARCHICAL_PARENT_SIZE,
    child_size: int = HIERARCHICAL_CHILD_SIZE,
    metadata: dict | None = None,
) -> tuple[list[Chunk], list[Chunk]]:
    """Create parent/child chunks, retaining source metadata and stable parent IDs."""
    if parent_size <= 0 or child_size <= 0:
        raise ValueError("parent_size and child_size must be positive")
    metadata = dict(metadata or {})
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not paragraphs:
        return [], []

    parent_texts: list[str] = []
    current = ""
    for paragraph in paragraphs:
        for piece in _split_oversize(paragraph, parent_size):
            candidate = f"{current}\n\n{piece}".strip() if current else piece
            if current and len(candidate) > parent_size:
                parent_texts.append(current)
                current = piece
            else:
                current = candidate
    if current:
        parent_texts.append(current)

    parents: list[Chunk] = []
    children: list[Chunk] = []
    source = str(metadata.get("source", "document"))
    for parent_index, parent_text in enumerate(parent_texts):
        digest = hashlib.sha256(f"{source}\0{parent_index}\0{parent_text}".encode()).hexdigest()[:16]
        parent_id = f"parent_{digest}"
        parent_meta = {**metadata, "chunk_type": "parent", "parent_id": parent_id, "chunk_index": parent_index}
        parents.append(Chunk(parent_text, parent_meta, parent_id))

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", parent_text) if s.strip()]
        child_parts: list[str] = []
        child_current = ""
        for sentence in sentences:
            for piece in _split_oversize(sentence, child_size):
                candidate = f"{child_current} {piece}".strip() if child_current else piece
                if child_current and len(candidate) > child_size:
                    child_parts.append(child_current)
                    child_current = piece
                else:
                    child_current = candidate
        if child_current:
            child_parts.append(child_current)
        for child_text in child_parts:
            children.append(Chunk(
                child_text,
                {**metadata, "chunk_type": "child", "chunk_index": len(children)},
                parent_id,
            ))
    return parents, children


def chunk_structure_aware(text: str, metadata: dict | None = None) -> list[Chunk]:
    metadata = dict(metadata or {})
    matches = list(re.finditer(r"(?m)^#{1,3}\s+.+$", text))
    if not matches:
        stripped = text.strip()
        return [Chunk(stripped, {**metadata, "section": "root", "strategy": "structure", "chunk_index": 0})] if stripped else []
    output: list[Chunk] = []
    prefix = text[: matches[0].start()].strip()
    if prefix:
        output.append(Chunk(prefix, {**metadata, "section": "root", "strategy": "structure", "chunk_index": 0}))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section_text = text[match.start() : end].strip()
        section = re.sub(r"^#{1,3}\s+", "", match.group()).strip()
        output.append(Chunk(section_text, {**metadata, "section": section, "strategy": "structure", "chunk_index": len(output)}))
    return output


def compare_strategies(documents: list[dict]) -> dict:
    def stats(chunks: list[Chunk]) -> dict:
        lengths = [len(chunk.text) for chunk in chunks]
        return {"count": len(lengths), "avg_len": round(sum(lengths) / len(lengths)) if lengths else 0,
                "min_len": min(lengths) if lengths else 0, "max_len": max(lengths) if lengths else 0}

    text = "\n\n".join(document["text"] for document in documents)
    parents, children = chunk_hierarchical(text, metadata={"source": "all"})
    return {"basic": stats(chunk_basic(text)), "semantic": stats(chunk_semantic(text)),
            "hierarchical": {**stats(children), "parents": len(parents)},
            "structure": stats(chunk_structure_aware(text))}
