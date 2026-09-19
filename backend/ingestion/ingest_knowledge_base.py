"""
Knowledge base ingestion.

Reads each role's source PDFs (data/knowledge_base/<file>.pdf), chunks
them, embeds the chunks, and stores them in a per-role ChromaDB
collection.

Chunking strategy (deliberate choices, explained for interview defense):
  - Token-aware sizing (via tiktoken) rather than raw character counts,
    so chunk boundaries respect roughly how the LLM "sees" text -- this
    keeps each chunk small enough to fit comfortably inside a prompt
    alongside several retrieved chunks, without truncation surprises.
  - ~300 token chunks with ~50 token overlap: large enough to preserve
    a full concept/paragraph's context (avoids splitting a definition
    from its explanation), small enough that retrieval stays precise
    (a giant chunk would "match" too many unrelated queries).
  - Overlap prevents an idea that spans a chunk boundary from being
    silently cut in half and losing meaning in both resulting chunks.

This script is safe to re-run: it skips any role collection that
already has data (see chroma_client.collection_exists_and_populated),
so it can also run automatically at backend startup without wasting
time/embedding cost.
"""
import sys
import uuid
from pathlib import Path

import tiktoken
from pypdf import PdfReader

# Allow running this script directly (python ingestion/ingest_knowledge_base.py)
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.roles import list_roles
from app.vectorstore.chroma_client import add_chunks, collection_exists_and_populated

KB_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"
CHUNK_SIZE_TOKENS = 300
CHUNK_OVERLAP_TOKENS = 50

_encoding = tiktoken.get_encoding("cl100k_base")


def extract_pages(pdf_path: Path) -> list[str]:
    """Returns list of page texts (index = page number - 1)."""
    reader = PdfReader(str(pdf_path))
    return [page.extract_text() or "" for page in reader.pages]


def chunk_page_text(text: str) -> list[str]:
    """Token-aware sliding-window chunking with overlap."""
    tokens = _encoding.encode(text)
    if not tokens:
        return []

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_SIZE_TOKENS, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = _encoding.decode(chunk_tokens).strip()
        if chunk_text:
            chunks.append(chunk_text)
        if end == len(tokens):
            break
        start = end - CHUNK_OVERLAP_TOKENS  # slide window back for overlap
    return chunks


def ingest_role(role) -> int:
    """Ingests all source files for one role. Returns number of chunks added."""
    if collection_exists_and_populated(role.collection_name):
        print(f"[skip] {role.label}: collection already populated")
        return 0

    total_added = 0
    for filename in role.source_files:
        pdf_path = KB_DIR / filename
        if not pdf_path.exists():
            print(f"[warn] {role.label}: missing source file {filename} (skipping)")
            continue

        pages = extract_pages(pdf_path)
        chunk_ids, chunk_texts, metadatas = [], [], []

        for page_num, page_text in enumerate(pages, start=1):
            for chunk in chunk_page_text(page_text):
                chunk_ids.append(str(uuid.uuid4()))
                chunk_texts.append(chunk)
                metadatas.append(
                    {"source_book": filename, "page_number": page_num, "role": role.id}
                )

        if chunk_texts:
            add_chunks(role.collection_name, chunk_ids, chunk_texts, metadatas)
            total_added += len(chunk_texts)
            print(f"[ok] {role.label}: {filename} -> {len(chunk_texts)} chunks")

    return total_added


def ensure_ingested() -> None:
    """Entry point used both by CLI and by the app startup hook."""
    for role in list_roles():
        ingest_role(role)


if __name__ == "__main__":
    ensure_ingested()
