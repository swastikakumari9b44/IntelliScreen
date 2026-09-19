# Submission Preparation Guide

## 1–8: Already covered in README.md
Setup instructions, environment variables, database setup, API documentation,
architecture explanation, and feature list all live in the main `README.md`.

## 9. Testing Instructions
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```
Manual end-to-end test checklist:
- [ ] Upload a real resume PDF, select each of the 4 roles once, confirm
      different skills are extracted per resume
- [ ] Confirm questions differ meaningfully between two different resumes
      for the *same* role (this is the single most important thing an
      evaluator will probe)
- [ ] Answer all questions in one session, confirm summary shows correct
      transcript and topic tags
- [ ] Restart the backend, confirm Past Sessions still shows prior sessions
      (validates Postgres durability, not just in-memory state)
- [ ] Try uploading a non-PDF file — confirm a clean error, not a crash
- [ ] Try submitting an empty answer — confirm client-side + server-side
      validation both catch it

## 10. Screenshots Checklist
Capture these for your submission/README:
- [ ] New Interview screen (empty state)
- [ ] Role dropdown expanded, showing all 4 roles
- [ ] Interview screen mid-flow with progress bar visible
- [ ] Summary screen showing full transcript + insights
- [ ] Past Sessions list with 2+ sessions
- [ ] FastAPI Swagger docs (`/docs`) — shows API design maturity well

## 11. Resume Bullet (short project description)
> Built an AI-powered candidate screening system using a Retrieval-Augmented
> Generation pipeline (FastAPI, ChromaDB, Groq/Llama) to dynamically generate
> role-specific technical interview questions grounded in resume content and
> a curated knowledge base; included full traceability from question to
> source document and a React dashboard for session management.

## 12. 30-Second Interview Explanation
> "I built a system that simulates a technical interview, but instead of
> using fixed questions, it generates them dynamically. A candidate uploads
> their resume and picks a role — the system extracts their skills, retrieves
> relevant passages from a role-specific textbook using a vector database,
> and feeds that context to an LLM to generate a grounded, non-generic
> question. Every question is traceable back to the exact source passage
> that produced it. It's a full-stack app — React frontend, FastAPI backend,
> Postgres for persistence, and ChromaDB for retrieval."

## 13. 2-Minute Interview Explanation
> "The core idea is a role-based screening interview where questions aren't
> pre-written — they're generated per-candidate using RAG.
>
> The flow starts when a candidate uploads a resume and picks a role — I
> support four roles, each mapped to a specific provided textbook so the
> knowledge base stays grounded rather than pulling from generic internet
> content. On upload, I parse the resume with pypdf and extract skills using
> a curated keyword vocabulary — I chose a rule-based approach over NLP/NER
> deliberately, since it's fast, deterministic, and easy to defend, and
> upgrading to NER later is a contained change.
>
> For question generation, I build a query from the candidate's skills and
> the selected role, embed it locally using sentence-transformers, and
> retrieve the top-k relevant chunks from that role's ChromaDB collection.
> Those chunks are then fed into an LLM prompt — I used Groq's free API with
> Llama 3.3 — with explicit instructions to avoid generic questions and stay
> grounded in the retrieved material.
>
> On the backend side, I separated the code into an API layer, a service
> layer, and a data layer. Routers only validate and delegate; all the real
> logic — resume parsing, retrieval, generation, session orchestration — lives
> in services. That separation is also why the LLM client is its own
> interface: if I wanted to swap Groq for OpenAI, it's a one-file change.
>
> For persistence, every question stores the IDs of the chunks that
> generated it, which gives full traceability — you can see exactly which
> page of which textbook produced each question. Sessions, questions, and
> answers are stored in Postgres via SQLAlchemy, and I rebuild the vector
> store automatically at startup since free hosting tiers often wipe local
> disk on redeploy — the knowledge base is static, so that's cheap to redo,
> while actual interview data stays safely in Postgres.
>
> The frontend is a React dashboard with three main flows: starting a new
> interview, walking through the Q&A, and viewing a structured summary with
> topics covered and the full transcript, plus a history view of past
> sessions."

## 14. Likely Interviewer Questions & Answers

**Q: Why did you choose token-based chunking with overlap instead of simpler fixed-character chunks?**
A: Character-based chunking doesn't correspond to how the LLM actually
consumes text, so chunk sizes become unpredictable relative to the model's
context window. Token-based chunking (via tiktoken) keeps sizes consistent
with the model's tokenizer. The overlap (50 tokens) exists so a concept
split across a chunk boundary — like a definition and the sentence
explaining it — isn't fully separated and losing meaning in both halves.

**Q: How do you ensure the generated questions are actually grounded and not hallucinated?**
A: Two layers: first, retrieval only returns real passages from the
ingested PDFs — there's no fallback to general knowledge if retrieval comes
back empty (it raises an error instead of silently generating an ungrounded
question). Second, the system prompt explicitly instructs the model to use
only the provided reference material and forbids inventing facts outside it.
It's not a perfect hallucination guarantee — no prompt-based approach is —
but it constrains the model's input tightly.

**Q: Why rule-based skill extraction instead of an NLP model?**
A: Given the scope and time constraints, a curated keyword vocabulary with
word-boundary matching is deterministic, fast, and fully explainable — I can
show exactly why any skill was or wasn't detected. An NER-based approach
would likely catch more nuance (multi-word phrasing, implied skills) but
adds a model dependency and less predictable behavior. It's a documented
upgrade path, not a permanent design ceiling.

**Q: What would you change if you had more time?**
A: Three things: implement the adaptive follow-up questions (the assignment
explicitly calls this out as valuable), add authentication so this could be
multi-tenant instead of open-access, and add Alembic migrations instead of
relying on `create_all()` for schema management as the data model evolves.

**Q: How does this scale if the knowledge base or user base grows?**
A: The service-layer separation means most components can scale
independently — swap SQLite/local Postgres for a managed Postgres cluster,
swap ChromaDB for a hosted vector DB (Pinecone/Weaviate) if the corpus grows
past what a single-node embedded store handles well, and the LLM client
abstraction means the generation step isn't tied to one provider. None of
that requires changing the API or service layer.

**Q: Why Groq instead of OpenAI?**
A: Practical constraint — no OpenAI key/budget available for this project.
Groq's free tier is fast and has no payment method requirement, which also
matters since this needs to be hosted on a free tier end-to-end. The LLM
client is abstracted, so this is a one-file change if that constraint
changes.

## Final Demo Checklist
Before recording:
- [ ] Run the full local setup from a clean clone (backend + frontend) to
      confirm the README instructions actually work
- [ ] Confirm `.env` files exist locally and are NOT committed (check `.gitignore`)
- [ ] Ingest the knowledge base once and confirm no errors in console
- [ ] Pre-load 1–2 sample resumes to use during the recording

During the demo video, show:
1. The Swagger docs (`/docs`) briefly — demonstrates API design
2. Uploading a resume + selecting a role
3. At least 2–3 generated questions, pointing out they reference specific
   concepts (not generic)
4. Answering and completing the interview
5. The summary screen with insights and full transcript
6. The Past Sessions view, proving persistence
7. (Optional but strong) Briefly open the database or a source chunk to show
   the `source_chunk_ids` traceability field in action
