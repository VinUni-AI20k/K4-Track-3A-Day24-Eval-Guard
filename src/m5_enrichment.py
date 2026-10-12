from __future__ import annotations

"""
Module 5: Enrichment Pipeline
==============================
Làm giàu chunks TRƯỚC khi embed: Summarize, HyQA, Contextual Prepend, Auto Metadata.

Test: pytest tests/test_m5.py
"""

import os, sys, re
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import lru_cache

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, GENERATION_MODEL as LLM_MODEL


@lru_cache(maxsize=1)
def get_client():
    from openai import OpenAI
    return OpenAI(timeout=90, max_retries=1)


@dataclass
class EnrichedChunk:
    """Chunk đã được làm giàu."""
    original_text: str
    enriched_text: str
    summary: str
    hypothesis_questions: list[str]
    auto_metadata: dict
    method: str  # "contextual", "summary", "hyqa", "full"


# ─── Technique 1: Chunk Summarization ────────────────────


def summarize_chunk(text: str) -> str:
    """
    Tạo summary ngắn cho chunk.
    Embed summary thay vì (hoặc cùng với) raw chunk → giảm noise.
    """
    if not text:
        return ""
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = get_client()
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "Tóm tắt đoạn văn sau trong 2-3 câu ngắn gọn bằng tiếng Việt."},
                    {"role": "user", "content": text},
                ],
                max_tokens=150,
                temperature=0,
            )
            content = resp.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception as e:
            pass

    # Extractive fallback (không cần API):
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    if sentences:
        s_part = ". ".join(sentences[:2])
        return s_part if s_part.endswith(".") else s_part + "."
    return text


# ─── Technique 2: Hypothesis Question-Answer (HyQA) ─────


def generate_hypothesis_questions(text: str, n_questions: int = 3) -> list[str]:
    """
    Generate câu hỏi mà chunk có thể trả lời.
    Index cả questions lẫn chunk → query match tốt hơn (bridge vocabulary gap).
    """
    if not text:
        return []
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = get_client()
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": f"Dựa trên đoạn văn, tạo {n_questions} câu hỏi mà đoạn văn có thể trả lời. Trả về mỗi câu hỏi trên 1 dòng."},
                    {"role": "user", "content": text},
                ],
                max_tokens=200,
                temperature=0,
            )
            raw = resp.choices[0].message.content.strip().split("\n")
            qs = [q.strip().lstrip("0123456789.-) ") for q in raw if q.strip()]
            if qs:
                return qs[:n_questions]
        except Exception as e:
            pass

    # Extractive fallback
    raw_sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if len(s.strip()) > 8]
    questions = []
    for s in raw_sentences[:n_questions]:
        questions.append(f"{s.rstrip(' .!?')} như thế nào?")
    if not questions:
        questions = ["Quy định này bao gồm những nội dung gì?"]
    return questions[:n_questions]


# ─── Technique 3: Contextual Prepend (Anthropic style) ──


def contextual_prepend(text: str, document_title: str = "") -> str:
    """
    Prepend context giải thích chunk nằm ở đâu trong document.
    Anthropic benchmark: giảm 49% retrieval failure (alone).
    """
    if not text:
        return ""
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = get_client()
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "Viết 1 câu ngắn mô tả đoạn văn này nằm ở đâu trong tài liệu và nói về chủ đề gì. Chỉ trả về 1 câu."},
                    {"role": "user", "content": f"Tài liệu: {document_title}\n\nĐoạn văn:\n{text}"},
                ],
                max_tokens=80,
                temperature=0,
            )
            context = resp.choices[0].message.content
            if context and context.strip():
                return f"{context.strip()}\n\n{text}"
        except Exception as e:
            pass

    prefix = f"Trích từ {document_title}. " if document_title else ""
    return f"{prefix}{text}"


# ─── Technique 4: Auto Metadata Extraction ──────────────


def extract_metadata(text: str) -> dict:
    """
    LLM extract metadata tự động: topic, entities, date_range, category.
    """
    if not text:
        return {"topic": "quy định nội bộ", "entities": [], "category": "policy", "language": "vi"}
    if OPENAI_API_KEY:
        try:
            import json as _json
            from openai import OpenAI
            client = get_client()
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": 'Trích xuất metadata từ đoạn văn. Trả về JSON: {"topic": "...", "entities": ["..."], "category": "policy|hr|it|finance", "language": "vi|en"}'},
                    {"role": "user", "content": text},
                ],
                max_tokens=150,
                temperature=0,
            )
            content = resp.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return _json.loads(content.strip())
        except Exception as e:
            pass

    return {"topic": "quy định nội bộ", "entities": [], "category": "policy", "language": "vi"}


# ─── Combined Single-Call Mode ───────────────────────────


def _enrich_single_call(text: str, source: str) -> dict:
    """Single LLM call to get summary + questions + context + metadata.

    ⚠️ Cost optimization: 1 API call thay vì 4 calls riêng lẻ.
    """
    if not text:
        return {}
    if OPENAI_API_KEY:
        try:
            import json as _json
            from openai import OpenAI
            client = get_client()
            prompt = (
                f"Phân tích đoạn văn sau từ tài liệu '{source}' và trả về DUY NHẤT một chuỗi JSON hợp lệ theo cấu trúc:\n"
                f"{{\n"
                f'  "summary": "Tóm tắt ngắn gọn 2-3 câu",\n'
                f'  "questions": ["Câu hỏi 1 mà đoạn văn giải đáp?", "Câu hỏi 2?", "Câu hỏi 3?"],\n'
                f'  "context": "1 câu mô tả đoạn văn nằm ở đâu trong tài liệu",\n'
                f'  "metadata": {{"topic": "...", "entities": ["..."], "category": "policy|hr|it|finance", "language": "vi|en"}}\n'
                f"}}\n\n"
                f"Đoạn văn:\n{text}"
            )
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia phân tích quy chế. Chỉ trả về JSON thuần, không kèm định dạng markdown hay giải thích."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=400,
                temperature=0,
            )
            content = resp.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            data = _json.loads(content.strip())
            if not isinstance(data, dict) or not isinstance(data.get("summary"), str) or not isinstance(data.get("context"), str) or not isinstance(data.get("metadata"), dict) or not isinstance(data.get("questions"), list) or not all(isinstance(q, str) for q in data["questions"]):
                raise ValueError("Invalid enrichment JSON schema")
            data["_status"] = "success"
            return data
        except Exception as e:
            pass

    # Extractive local fallback when no API key / quota exhausted
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    summary = ". ".join(sentences[:2]) + ("." if sentences and not sentences[:2][-1].endswith(".") else "") if sentences else text
    raw_s = [s.strip() for s in re.split(r'[.!?\n]', text) if len(s.strip()) > 8]
    questions = [f"{s.rstrip(' .!?')} như thế nào?" for s in raw_s[:3]] or ["Quy định này bao gồm những nội dung gì?"]
    context = f"Trích từ tài liệu {source}." if source else ""
    return {
        "_status": "fallback",
        "summary": summary,
        "questions": questions,
        "context": context,
        "metadata": {"topic": "quy định nội bộ", "category": "policy", "language": "vi"}
    }


# ─── Full Enrichment Pipeline ────────────────────────────


def enrich_chunks(
    chunks: list[dict],
    methods: list[str] | None = None,
) -> list[EnrichedChunk]:
    """
    Chạy enrichment pipeline trên danh sách chunks. (Đã implement sẵn — dùng functions ở trên)

    Có 2 chế độ:
    - methods cụ thể (["summary"], ["contextual"]...): gọi từng function riêng (tốt cho học/debug)
    - methods=["combined"] hoặc None: 1 API call duy nhất cho tất cả (tốt cho production)

    Args:
        chunks: List of {"text": str, "metadata": dict}
        methods: Default None → combined mode (1 call/chunk).
                 Options: "summary", "hyqa", "contextual", "metadata", "combined"
    """
    if methods is None:
        methods = ["combined"]

    use_combined = "combined" in methods

    def _enrich_one(chunk: dict) -> EnrichedChunk:
        text = chunk["text"]
        source = chunk.get("metadata", {}).get("source", "")

        if use_combined:
            result = _enrich_single_call(text, source)
            summary = result.get("summary", "")
            questions = result.get("questions", [])
            context_line = result.get("context", "")
            enriched_text = f"{context_line}\n\n{text}" if context_line else text
            auto_meta = {**result.get("metadata", {}), "enrichment_status": result.get("_status", "unknown")}
        else:
            summary = summarize_chunk(text) if "summary" in methods else ""
            questions = generate_hypothesis_questions(text) if "hyqa" in methods else []
            enriched_text = contextual_prepend(text, source) if "contextual" in methods else text
            auto_meta = extract_metadata(text) if "metadata" in methods else {}

        additions = ([summary] if summary else []) + questions[:3]
        enriched_text = "\n\n".join([enriched_text, *additions])
        return EnrichedChunk(
            original_text=text,
            enriched_text=enriched_text,
            summary=summary,
            hypothesis_questions=questions,
            auto_metadata={**auto_meta, **chunk.get("metadata", {}), "original_text": text},
            method="+".join(methods),
        )

    # pool.map giữ đúng thứ tự và số lượng chunks đầu vào.
    with ThreadPoolExecutor(max_workers=int(os.getenv("ENRICH_WORKERS", "8"))) as pool:
        enriched = list(pool.map(_enrich_one, chunks))

    fallbacks = sum(1 for e in enriched if e.auto_metadata.get("enrichment_status") == "fallback")
    print(f"  Enriched {len(enriched)}/{len(chunks)} chunks (extractive fallback: {fallbacks})", flush=True)
    return enriched


# ─── Main ────────────────────────────────────────────────

if __name__ == "__main__":
    sample = "Nhân viên chính thức được nghỉ phép năm 12 ngày làm việc mỗi năm. Số ngày nghỉ phép tăng thêm 1 ngày cho mỗi 5 năm thâm niên công tác."

    print("=== Enrichment Pipeline Demo ===\n")
    print(f"Original: {sample}\n")

    s = summarize_chunk(sample)
    print(f"Summary: {s}\n")

    qs = generate_hypothesis_questions(sample)
    print(f"HyQA questions: {qs}\n")

    ctx = contextual_prepend(sample, "Sổ tay nhân viên VinUni 2024")
    print(f"Contextual: {ctx}\n")

    meta = extract_metadata(sample)
    print(f"Auto metadata: {meta}")
