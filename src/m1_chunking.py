from __future__ import annotations

import os
import glob
from dataclasses import dataclass, field
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR, HIERARCHICAL_PARENT_SIZE, HIERARCHICAL_CHILD_SIZE


@dataclass
class ParentChunk:
    text: str
    metadata: dict = field(default_factory=dict)
    parent_id: str = ""


@dataclass
class ChildChunk:
    text: str
    metadata: dict = field(default_factory=dict)
    parent_id: str = ""


def load_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """Tải toàn bộ tài liệu từ DATA_DIR (.md, .txt, .pdf)."""
    documents: list[dict] = []
    if not os.path.exists(data_dir):
        return documents

    for filepath in glob.glob(os.path.join(data_dir, "*")):
        path = Path(filepath)
        filename = path.name
        ext = path.suffix.lower()

        if ext in [".md", ".txt"]:
            try:
                content = path.read_text(encoding="utf-8")
                if content.strip():
                    documents.append({
                        "text": content,
                        "metadata": {
                            "source": filename,
                            "filename": filename,
                            "file_type": ext[1:],
                        }
                    })
            except Exception as e:
                print(f"Error reading {filename}: {e}")

        elif ext == ".pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(path))
                text_pages = []
                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_pages.append(page_text)
                full_text = "\n\n".join(text_pages)
                if full_text.strip():
                    documents.append({
                        "text": full_text,
                        "metadata": {
                            "source": filename,
                            "filename": filename,
                            "file_type": "pdf",
                            "pages": len(reader.pages),
                        }
                    })
            except Exception as e:
                print(f"Error reading PDF {filename}: {e}")

    return documents


def chunk_hierarchical(text: str, metadata: dict = None) -> tuple[list[ParentChunk], list[ChildChunk]]:
    """Phân cấp tài liệu thành Parent chunks (~2048 chars) và Child chunks (~256 chars)."""
    meta = metadata.copy() if metadata else {}
    src = meta.get("source", "doc")

    parents: list[ParentChunk] = []
    children: list[ChildChunk] = []

    # Chia parent chunks
    step_parent = HIERARCHICAL_PARENT_SIZE
    step_child = HIERARCHICAL_CHILD_SIZE

    for p_idx, p_start in enumerate(range(0, len(text), step_parent)):
        p_text = text[p_start : p_start + step_parent].strip()
        if not p_text:
            continue
        p_id = f"{src}_p{p_idx}"
        p_meta = {**meta, "parent_id": p_id, "chunk_level": "parent"}
        parent = ParentChunk(text=p_text, metadata=p_meta, parent_id=p_id)
        parents.append(parent)

        # Chia children chunks trong parent
        for c_idx, c_start in enumerate(range(0, len(p_text), step_child)):
            c_text = p_text[c_start : c_start + step_child].strip()
            if not c_text:
                continue
            c_id = f"{p_id}_c{c_idx}"
            c_meta = {**meta, "child_id": c_id, "parent_id": p_id, "chunk_level": "child"}
            child = ChildChunk(text=c_text, metadata=c_meta, parent_id=p_id)
            children.append(child)

    return parents, children
