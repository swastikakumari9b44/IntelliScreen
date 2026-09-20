"""
Lightweight vector store (replaces ChromaDB).

Why: ChromaDB pulls in a large transitive dependency tree (grpc,
opentelemetry, a Kubernetes client, onnxruntime, posthog analytics) that
gets imported at startup regardless of whether those features are used --
on a memory-constrained host (e.g. Render's free 512MB tier), this
overhead alone can be a meaningful chunk of the budget.

Since our knowledge base is static (a fixed set of textbooks that never
changes), there's no need for a full vector database with live-write
support. Embeddings are precomputed OFFLINE (see
`scripts/precompute_embeddings.py`, run locally, never on the deployed
server) and saved as plain files. At runtime, the server just loads a
small numpy array and a JSON file per role and does cosine similarity
with numpy -- no embedding computation of the knowledge base happens on
the server at all, and no heavy vector-DB dependency is required.

File layout per role (under PRECOMPUTED_DIR/<role_id>/):
  - embeddings.npy   -- float32 array, shape (num_chunks, embedding_dim),
                         L2-normalized so cosine similarity = dot product
  - chunks.json      -- list of {id, text, metadata}, same order as rows
                         in embeddings.npy
"""
import json
from pathlib import Path

import numpy as np

from app.config import get_settings

settings = get_settings()

# Cache loaded role stores in memory so repeated queries don't re-read
# from disk -- these are small (a few MB per role at most), so caching
# all of them is cheap relative to the memory budget.
_role_cache: dict[str, dict] = {}


def _role_dir(role_id: str) -> Path:
    return Path(settings.precomputed_dir) / role_id


def _load_role_store(role_id: str) -> dict | None:
    if role_id in _role_cache:
        return _role_cache[role_id]

    role_dir = _role_dir(role_id)
    embeddings_path = role_dir / "embeddings.npy"
    chunks_path = role_dir / "chunks.json"

    if not embeddings_path.exists() or not chunks_path.exists():
        return None

    embeddings = np.load(embeddings_path)
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    store = {"embeddings": embeddings, "chunks": chunks}
    _role_cache[role_id] = store
    return store


def is_role_ingested(role_id: str) -> bool:
    return _load_role_store(role_id) is not None


def query(role_id: str, query_embedding: np.ndarray, top_k: int) -> list[dict]:
    """
    Returns the top_k most similar chunks: [{id, text, metadata, score}, ...]
    Returns [] if this role has no precomputed embeddings available.
    """
    store = _load_role_store(role_id)
    if store is None:
        return []

    embeddings = store["embeddings"]
    chunks = store["chunks"]

    # query_embedding is expected to already be L2-normalized (see
    # embeddings.embed_query), matching how embeddings.npy was saved --
    # so a plain dot product gives cosine similarity directly.
    scores = embeddings @ query_embedding
    k = min(top_k, len(chunks))
    top_indices = np.argpartition(-scores, k - 1)[:k]
    top_indices = top_indices[np.argsort(-scores[top_indices])]

    results = []
    for idx in top_indices:
        chunk = chunks[int(idx)]
        results.append({
            "id": chunk["id"],
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "score": float(scores[idx]),
        })
    return results
