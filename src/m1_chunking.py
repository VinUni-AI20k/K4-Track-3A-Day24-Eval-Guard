"""Module 1: Document loading and hierarchical chunking.
Conforms to doc/PIPELINE_INTERFACE.md.
"""
from __future__ import annotations

import os
import glob
from dataclasses import dataclass, field
from types import SimpleNamespace
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR, HIERARCHICAL_PARENT_SIZE, HIERARCHICAL_CHILD_SIZE


@dataclass
class ChildChunk:
    text: str
    metadata: dict = field(default_factory=dict)
    parent_id: str = ""


@dataclass
class ParentChunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


def load_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """Đọc toàn bộ tài liệu (.md, .pdf) từ data_dir.
    
    Returns:
        list of dict: [{"text": str, "metadata": {"source": filename, ...}}]
    """
    documents = []
    
    # 1. Đọc tất cả markdown files
    md_files = glob.glob(os.path.join(data_dir, "*.md"))
    for file_path in md_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if content.strip():
                documents.append({
                    "text": content,
                    "metadata": {
                        "source": os.path.basename(file_path),
                        "file_type": "markdown",
                    }
                })
        except Exception as e:
            print(f"Warning reading {file_path}: {e}")

    # 2. Đọc file PDF nếu có pypdf
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    if pdf_files:
        try:
            import pypdf
            for file_path in pdf_files:
                try:
                    reader = pypdf.PdfReader(file_path)
                    text_parts = []
                    for idx, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    full_text = "\n\n".join(text_parts)
                    if full_text.strip():
                        documents.append({
                            "text": full_text,
                            "metadata": {
                                "source": os.path.basename(file_path),
                                "file_type": "pdf",
                                "page_count": len(reader.pages),
                            }
                        })
                except Exception as e:
                    print(f"Warning reading PDF {file_path}: {e}")
        except ImportError:
            print("pypdf not installed, skipping PDF reading")

    return documents


def chunk_hierarchical(text: str, metadata: dict = None,
                       parent_size: int = HIERARCHICAL_PARENT_SIZE,
                       child_size: int = HIERARCHICAL_CHILD_SIZE) -> tuple[list[ParentChunk], list[ChildChunk]]:
    """Phân cấp tài liệu thành parent chunks và child chunks.
    
    Mỗi child chunk chứa:
        .text: str
        .metadata: dict
        .parent_id: str
        
    Returns:
        (parents, children)
    """
    if metadata is None:
        metadata = {}

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()] if text.strip() else []

    parents: list[ParentChunk] = []
    children: list[ChildChunk] = []

    current_parent_text = []
    current_parent_len = 0
    parent_idx = 0

    def flush_parent(p_idx: int, p_text: str):
        p_id = f"{metadata.get('source', 'doc')}_p{p_idx}"
        parent_obj = ParentChunk(id=p_id, text=p_text, metadata={**metadata, "parent_id": p_id})
        parents.append(parent_obj)

        # Tạo child chunks từ parent_text
        c_idx = 0
        p_paras = [p.strip() for p in p_text.split("\n") if p.strip()]
        curr_c_text = []
        curr_c_len = 0

        for line in p_paras:
            if curr_c_len + len(line) > child_size and curr_c_text:
                c_content = " ".join(curr_c_text)
                children.append(ChildChunk(
                    text=c_content,
                    metadata={**metadata, "parent_id": p_id, "child_index": c_idx},
                    parent_id=p_id
                ))
                c_idx += 1
                curr_c_text = [line]
                curr_c_len = len(line)
            else:
                curr_c_text.append(line)
                curr_c_len += len(line)

        if curr_c_text:
            c_content = " ".join(curr_c_text)
            children.append(ChildChunk(
                text=c_content,
                metadata={**metadata, "parent_id": p_id, "child_index": c_idx},
                parent_id=p_id
            ))

    for p in paragraphs:
        if current_parent_len + len(p) > parent_size and current_parent_text:
            flush_parent(parent_idx, "\n\n".join(current_parent_text))
            parent_idx += 1
            current_parent_text = [p]
            current_parent_len = len(p)
        else:
            current_parent_text.append(p)
            current_parent_len += len(p)

    if current_parent_text:
        flush_parent(parent_idx, "\n\n".join(current_parent_text))

    return parents, children

