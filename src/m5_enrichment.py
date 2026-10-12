"""Module 5: Chunk enrichment.
Conforms to doc/PIPELINE_INTERFACE.md.
"""
from __future__ import annotations

from types import SimpleNamespace


def enrich_chunks(chunks: list[dict]) -> list[SimpleNamespace]:
    """Làm giàu ngữ cảnh cho từng chunk.
    
    Yêu cầu giao diện:
        - Giữ nguyên số lượng và thứ tự đầu vào.
        - Mỗi phần tử trả về có:
            .enriched_text: str
            .auto_metadata: dict
            
    Returns:
        list of objects (SimpleNamespace)
    """
    enriched = []
    for c in chunks:
        raw_text = c.get("text", "")
        meta = c.get("metadata", {})
        source_name = meta.get("source", "document")
        parent_id = meta.get("parent_id", "")
        
        # Thêm header ngữ cảnh nguồn để embedding/search chính xác hơn
        enriched_text = f"[Nguồn: {source_name}] {raw_text}"
        auto_meta = {
            "source_doc": source_name,
            "parent_id": parent_id,
            "char_count": len(raw_text),
            "word_count": len(raw_text.split()),
        }
        
        enriched.append(SimpleNamespace(
            enriched_text=enriched_text,
            auto_metadata=auto_meta,
        ))
        
    return enriched

