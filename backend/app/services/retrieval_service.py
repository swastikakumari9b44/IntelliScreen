"""
Retrieval service (the "R" in RAG).

Responsible for turning (role, candidate skills, topics already asked)
into a query, and retrieving the most relevant knowledge-base chunks
for that role's ChromaDB collection.
"""
from app.config import get_settings
from app.roles import get_role
from app.vectorstore import chroma_client

settings = get_settings()


def build_query(role_id: str, skills: list[str], already_asked_topics: list[str]) -> str:
    """
    Constructs a retrieval query grounded in the resume and role.

    Why this shape: naming the role plus a rotating slice of the
    candidate's own skills keeps queries specific to the candidate
    (satisfying "resume should meaningfully influence topic selection")
    while `already_asked_topics` steers retrieval away from repeating
    the same chunk across questions in one session.
    """
    role = get_role(role_id)
    role_label = role.label if role else role_id

    skill_part = ", ".join(skills[:5]) if skills else "general fundamentals"
    query = f"{role_label} interview topics related to: {skill_part}."

    if already_asked_topics:
        avoid = ", ".join(already_asked_topics[-3:])
        query += f" Avoid repeating these already-covered topics: {avoid}."

    return query


def retrieve_context(role_id: str, query: str, top_k: int | None = None) -> list[dict]:
    """
    Returns the top_k most relevant chunks for this role's knowledge
    base: [{id, text, metadata, distance}, ...]. Empty list if nothing
    is retrievable (caller must handle this -- see question_gen_service
    fallback behavior).
    """
    role = get_role(role_id)
    if role is None:
        return []

    k = top_k or settings.retrieval_top_k
    return chroma_client.query(role.collection_name, query, top_k=k)
