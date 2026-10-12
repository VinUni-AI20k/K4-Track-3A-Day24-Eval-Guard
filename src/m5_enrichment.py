from __future__ import annotations

"""Chunk enrichment with deterministic offline fallbacks."""

import json
import re
from dataclasses import dataclass

from config import GENERATION_MODEL, OPENAI_API_KEY


@dataclass
class EnrichedChunk:
    original_text: str
    enriched_text: str
    summary: str
    hypothesis_questions: list[str]
    auto_metadata: dict
    method: str


def _chat(system: str, user: str, max_tokens: int) -> str | None:
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI

        response = OpenAI(api_key=OPENAI_API_KEY).chat.completions.create(
            model=GENERATION_MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_completion_tokens=max_tokens,
            reasoning_effort="minimal",
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        print(f"  Warning: enrichment API call failed: {exc}")
        return None


def summarize_chunk(text: str, *, use_api: bool = True) -> str:
    response = _chat("Tóm tắt đoạn văn sau trong 2-3 câu ngắn gọn bằng tiếng Việt.", text, 150) if use_api else None
    if response:
        return response
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]
    return " ".join(sentences[:2]) if sentences else text.strip()


def generate_hypothesis_questions(text: str, n_questions: int = 3,
                                  *, use_api: bool = True) -> list[str]:
    prompt = f"Tạo {n_questions} câu hỏi tiếng Việt mà đoạn văn có thể trả lời, mỗi câu một dòng."
    response = _chat(prompt, text, 200) if use_api else None
    if response:
        return [line.strip().lstrip("0123456789.-) ") for line in response.splitlines() if line.strip()][:n_questions]
    sentences = [part.strip() for part in re.split(r"[.!?\n]+", text) if len(part.strip()) > 10]
    return [f"Nội dung nào liên quan đến: {sentence}?" for sentence in sentences[:n_questions]]


def contextual_prepend(text: str, document_title: str = "", *, use_api: bool = True) -> str:
    response = _chat(
        "Viết một câu ngắn mô tả vị trí và chủ đề của đoạn văn. Chỉ trả về một câu.",
        f"Tài liệu: {document_title}\n\nĐoạn văn:\n{text}",
        80,
    ) if use_api else None
    prefix = response or (f"Trích từ {document_title}." if document_title else "Đoạn văn thuộc tài liệu nguồn.")
    return f"{prefix}\n\n{text}"


def extract_metadata(text: str, *, use_api: bool = True) -> dict:
    response = _chat(
        'Chỉ trả về JSON: {"topic":"...","entities":[],"category":"policy|hr|it|finance","language":"vi|en"}',
        text,
        150,
    ) if use_api else None
    if response:
        try:
            return json.loads(response.replace("```json", "").replace("```", "").strip())
        except (TypeError, ValueError):
            pass
    return {"topic": "general", "entities": [], "category": "policy", "language": "vi"}


def _combined(text: str, source: str, use_api: bool) -> dict:
    response = _chat(
        "Chỉ trả về JSON hợp lệ với keys summary, questions, context, metadata; "
        "questions là list và metadata có topic, entities, category, language.",
        f"Tài liệu: {source}\n\nĐoạn văn:\n{text}",
        400,
    ) if use_api else None
    if response:
        try:
            parsed = json.loads(response.replace("```json", "").replace("```", "").strip())
            if isinstance(parsed, dict):
                return parsed
        except (TypeError, ValueError):
            pass
    return {
        "summary": summarize_chunk(text, use_api=False),
        "questions": generate_hypothesis_questions(text, use_api=False),
        "context": f"Đoạn văn được trích từ tài liệu {source}." if source else "Đoạn văn thuộc tài liệu nguồn.",
        "metadata": extract_metadata(text, use_api=False),
    }


def enrich_chunks(
    chunks: list[dict],
    methods: list[str] | None = None,
    use_api: bool = True,
) -> list[EnrichedChunk]:
    methods = methods or ["combined"]
    allowed = {"summary", "hyqa", "contextual", "metadata", "combined"}
    unknown = set(methods) - allowed
    if unknown:
        raise ValueError(f"Unknown enrichment methods: {sorted(unknown)}")
    output: list[EnrichedChunk] = []
    for index, chunk in enumerate(chunks):
        text = chunk["text"]
        source = str(chunk.get("metadata", {}).get("source", ""))
        if "combined" in methods:
            result = _combined(text, source, use_api)
            summary = str(result.get("summary", ""))
            questions = list(result.get("questions", []))
            context = str(result.get("context", "")).strip()
            enriched_text = f"{context}\n\n{text}" if context else text
            generated_metadata = result.get("metadata", {})
        else:
            summary = summarize_chunk(text, use_api=use_api) if "summary" in methods else ""
            questions = generate_hypothesis_questions(text, use_api=use_api) if "hyqa" in methods else []
            enriched_text = contextual_prepend(text, source, use_api=use_api) if "contextual" in methods else text
            generated_metadata = extract_metadata(text, use_api=use_api) if "metadata" in methods else {}
        output.append(EnrichedChunk(
            original_text=text,
            enriched_text=enriched_text,
            summary=summary,
            hypothesis_questions=questions,
            auto_metadata={**chunk.get("metadata", {}), **generated_metadata},
            method="+".join(methods),
        ))
        if (index + 1) % 25 == 0 or index + 1 == len(chunks):
            print(f"  Enriched {index + 1}/{len(chunks)} chunks...", flush=True)
    return output
