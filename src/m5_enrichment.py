from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY


@dataclass
class EnrichedChunk:
    enriched_text: str
    auto_metadata: dict = field(default_factory=dict)


def enrich_chunks(chunks: list[dict]) -> list[EnrichedChunk]:
    """Làm giàu chunk văn bản bằng tóm tắt / metadata.
    
    Theo doc/PIPELINE_INTERFACE.md:
    Trả về [] là fallback dùng chunks gốc an toàn nếu không có API key hoặc không muốn tốn chi phí.
    """
    if not OPENAI_API_KEY:
        return []

    # Fallback dùng chunks gốc để tiết kiệm chi phí và thời gian chạy nhanh
    # Nếu cần kích hoạt enrichment thật:
    return []
