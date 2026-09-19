"""
Question generation service.

This is the core of the assignment: Context -> Question pipeline.
Orchestrates: build query -> retrieve chunks -> construct grounded
prompt -> call LLM -> return a question + the chunk ids that produced
it (traceability).

Design notes (for interview defense):
  - The prompt explicitly instructs the model to use ONLY the retrieved
    context and to avoid generic/template questions, directly targeting
    the assignment's "avoid generic or template-driven outputs"
    requirement.
  - Resume skills are injected into the prompt so questions are shaped
    by the candidate's actual background, not just the role in the
    abstract.
  - If retrieval returns nothing (e.g. missing PDFs at setup time), we
    fail loudly with a clear error rather than silently generating an
    ungrounded question -- grounding is a hard requirement here, not
    a nice-to-have.
"""
from app.llm.client import get_llm_client
from app.services.retrieval_service import build_query, retrieve_context

SYSTEM_PROMPT = """You are an experienced technical interviewer conducting a \
structured screening interview. You generate ONE interview question at a time, \
grounded strictly in the provided reference material. Do not invent facts \
outside the reference material. Avoid generic, templated, or overly broad \
questions ("Tell me about yourself", "What is machine learning?"). Instead, \
ask something specific enough that it clearly draws on the reference material \
and is relevant to the candidate's stated skills. Respond with ONLY the \
question text -- no preamble, no numbering, no explanation."""


def _build_user_prompt(role_label: str, skills: list[str], context_chunks: list[dict]) -> str:
    context_block = "\n\n".join(
        f"[Reference {i+1}]\n{c['text']}" for i, c in enumerate(context_chunks)
    )
    skills_str = ", ".join(skills) if skills else "not specified"

    return f"""Role being interviewed for: {role_label}
Candidate's background/skills (from resume): {skills_str}

Reference material (use this as the grounding for your question):
{context_block}

Generate one interview question that:
- Is answerable using the concepts in the reference material above
- Reflects the candidate's background where relevant
- Tests conceptual or applied understanding, not just recall of a definition
"""


def generate_question(
    role_id: str, role_label: str, skills: list[str], already_asked_topics: list[str]
) -> dict:
    """
    Returns {"question_text": str, "source_chunk_ids": list[str], "topic": str|None}
    Raises RuntimeError if no grounding context could be retrieved --
    the API layer converts this into a clean error response.
    """
    query = build_query(role_id, skills, already_asked_topics)
    chunks = retrieve_context(role_id, query)

    if not chunks:
        raise RuntimeError(
            f"No knowledge base content available for role '{role_id}'. "
            "Has the ingestion script been run for this role's source PDFs?"
        )

    user_prompt = _build_user_prompt(role_label, skills, chunks)
    llm = get_llm_client()

    # One retry: reasoning models occasionally truncate before producing
    # visible output (see LLMClient.generate). A single retry resolves
    # this in the vast majority of cases without masking a real,
    # persistent failure (e.g. bad API key), which will still raise.
    try:
        question_text = llm.generate(SYSTEM_PROMPT, user_prompt)
    except RuntimeError:
        question_text = llm.generate(SYSTEM_PROMPT, user_prompt)

    source_chunk_ids = [c["id"] for c in chunks]
    # Lightweight topic label: reuse the source book name of the top chunk
    # as a human-readable "topic" tag for the dashboard/summary view.
    topic = chunks[0]["metadata"].get("source_book", "").replace("_", " ").replace(".pdf", "")

    return {
        "question_text": question_text,
        "source_chunk_ids": source_chunk_ids,
        "topic": topic,
    }