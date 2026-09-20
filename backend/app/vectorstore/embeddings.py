"""
Embedding client (fastembed -- ONNX-based, no torch).

Why fastembed instead of sentence-transformers: sentence-transformers
pulls in torch as a dependency, which is a large runtime (even the
CPU-only build) that meaningfully increases both install size and
resident memory. fastembed uses ONNX Runtime with small, quantized
models instead -- functionally similar embedding quality for this
project's needs, at a fraction of the memory footprint. This matters
because the app needs to run comfortably inside a 512MB memory ceiling
on free hosting tiers.

The model used here must match the model used by
`scripts/precompute_embeddings.py` (the offline script that generates
the committed embedding artifacts) -- if they don't match, query
embeddings won't be comparable to the precomputed knowledge-base
embeddings.
"""
import numpy as np
from fastembed import TextEmbedding

from app.config import get_settings

settings = get_settings()

_model: TextEmbedding | None = None


def _get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=settings.embedding_model)
    return _model


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    return vec if norm == 0 else vec / norm


def embed_query(text: str) -> np.ndarray:
    """
    Embeds a single query string and L2-normalizes it, matching how
    embeddings.npy was precomputed -- so retrieval can use a plain dot
    product for cosine similarity.
    """
    model = _get_model()
    vec = next(model.embed([text]))
    return _normalize(np.asarray(vec, dtype=np.float32))
