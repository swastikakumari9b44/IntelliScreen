"""
ChromaDB client wrapper.

Why a wrapper: isolates all Chroma-specific API calls in one place, and
gives us a single spot to reason about persistence. Chroma persists to
local disk (CHROMA_PERSIST_DIR). On free hosting tiers that disk may be
ephemeral across redeploys, so `ensure_ingested()` (called at app
startup, see ingestion_runner.py) rebuilds any missing collection from
the source PDFs automatically -- the knowledge base is static, so
rebuilding on startup is cheap and removes any dependency on durable
disk for this data. Only interview data (sessions/Q&A) needs durable
storage, and that lives in Postgres, not here.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.vectorstore.embeddings import embed_texts

settings = get_settings()

_client: chromadb.ClientAPI | None = None


def get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def collection_exists_and_populated(collection_name: str) -> bool:
    client = get_client()
    try:
        collection = client.get_collection(collection_name)
    except Exception:
        return False
    return collection.count() > 0


def create_or_get_collection(collection_name: str):
    return get_client().get_or_create_collection(collection_name)


def add_chunks(
    collection_name: str,
    chunk_ids: list[str],
    chunk_texts: list[str],
    metadatas: list[dict],
) -> None:
    collection = create_or_get_collection(collection_name)
    embeddings = embed_texts(chunk_texts)
    collection.add(
        ids=chunk_ids,
        documents=chunk_texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query(collection_name: str, query_text: str, top_k: int) -> list[dict]:
    """
    Returns a list of {id, text, metadata, distance} for the top_k most
    relevant chunks. Returns [] gracefully if the collection doesn't
    exist yet (defensive -- should not happen after startup ingestion).
    """
    try:
        collection = get_client().get_collection(collection_name)
    except Exception:
        return []

    query_embedding = embed_texts([query_text])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    output = []
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    for i in range(len(ids)):
        output.append(
            {"id": ids[i], "text": docs[i], "metadata": metas[i], "distance": dists[i]}
        )
    return output
