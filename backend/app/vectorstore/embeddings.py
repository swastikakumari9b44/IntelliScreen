"""
Embedding client.

Why local (sentence-transformers) instead of an API: no key required,
free, and light enough (~80MB model) to run inside a free-tier hosted
backend. Kept behind a thin wrapper so it could be swapped for an API
based embedding model later without touching callers.
"""
from sentence_transformers import SentenceTransformer

from app.config import get_settings

settings = get_settings()

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Used for both KB chunks and query text."""
    model = _get_model()
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
