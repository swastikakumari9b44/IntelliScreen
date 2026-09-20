"""
Offline embedding precomputation.

RUN THIS LOCALLY ONLY -- never on the deployed server. This is the key
piece that makes free-tier hosting viable: since the knowledge base
(the 7 textbooks) is static, there is no reason to pay the memory/compute
cost of chunking + embedding it on every deploy. Instead:

  1. You run this script once on your own machine (where memory isn't
     constrained to 512MB).
  2. It chunks every book, embeds every chunk with fastembed, and saves
     the results as small files under backend/data/precomputed/<role_id>/.
  3. You commit those files to git.
  4. The deployed server just loads these precomputed files at query
     time -- no PDF parsing, no chunking, no embedding-the-whole-book
     computation ever happens in the deployed process.

Re-run this locally whenever you change CHUNK_SIZE_TOKENS,
CHUNK_OVERLAP_TOKENS, the embedding model, or the source PDFs.

Usage:
    cd backend
    python scripts/precompute_embeddings.py
"""
import json
import sys
import uuid
from pathlib import Path

import numpy as np
import tiktoken
from fastembed import TextEmbedding
from pypdf import PdfReader

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.roles import list_roles

settings = get_settings()

KB_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / Path(settings.precomputed_dir)

CHUNK_SIZE_TOKENS = 300
CHUNK_OVERLAP_TOKENS = 50
EMBED_BATCH_SIZE = 32

_encoding = tiktoken.get_encoding("cl100k_base")


def extract_pages(pdf_path: Path):
    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        yield page.extract_text() or ""


def chunk_page_text(text: str) -> list[str]:
    """Token-aware sliding-window chunking with overlap (see README for
    the reasoning behind these specific parameters)."""
    tokens = _encoding.encode(text)
    if not tokens:
        return []
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_SIZE_TOKENS, len(tokens))
        chunk_text = _encoding.decode(tokens[start:end]).strip()
        if chunk_text:
            chunks.append(chunk_text)
        if end == len(tokens):
            break
        start = end - CHUNK_OVERLAP_TOKENS
    return chunks


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


def precompute_role(role, model: TextEmbedding) -> int:
    role_out_dir = OUTPUT_DIR / role.id
    role_out_dir.mkdir(parents=True, exist_ok=True)

    all_chunks: list[dict] = []
    all_vectors: list[np.ndarray] = []

    for filename in role.source_files:
        pdf_path = KB_DIR / filename
        if not pdf_path.exists():
            print(f"[warn] {role.label}: missing source file {filename} (skipping)")
            continue

        pending_texts, pending_meta = [], []

        def flush():
            if not pending_texts:
                return
            vectors = list(model.embed(pending_texts))
            for text, meta, vec in zip(pending_texts, pending_meta, vectors):
                all_chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": text,
                    "metadata": meta,
                })
                all_vectors.append(np.asarray(vec, dtype=np.float32))
            pending_texts.clear()
            pending_meta.clear()

        file_chunk_count = 0
        for page_num, page_text in enumerate(extract_pages(pdf_path), start=1):
            for chunk in chunk_page_text(page_text):
                pending_texts.append(chunk)
                pending_meta.append(
                    {"source_book": filename, "page_number": page_num, "role": role.id}
                )
                file_chunk_count += 1
                if len(pending_texts) >= EMBED_BATCH_SIZE:
                    flush()
        flush()

        print(f"[ok] {role.label}: {filename} -> {file_chunk_count} chunks")

    if not all_chunks:
        print(f"[skip] {role.label}: no chunks produced (check source files)")
        return 0

    embeddings = normalize_rows(np.vstack(all_vectors))
    np.save(role_out_dir / "embeddings.npy", embeddings)
    with open(role_out_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f)

    print(f"[saved] {role.label}: {len(all_chunks)} chunks -> {role_out_dir}")
    return len(all_chunks)


def main():
    print(f"Loading embedding model: {settings.embedding_model}")
    model = TextEmbedding(model_name=settings.embedding_model)

    total = 0
    for role in list_roles():
        total += precompute_role(role, model)

    print(f"\nDone. {total} total chunks precomputed across all roles.")
    print(f"Output directory: {OUTPUT_DIR}")
    print("Remember to commit this directory to git.")


if __name__ == "__main__":
    main()
