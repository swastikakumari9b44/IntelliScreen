# AI-Powered Role-Based Candidate Screening System

A RAG-powered system that simulates a structured technical interview: it
parses a candidate's resume, retrieves grounded context from a role-specific
knowledge base (the provided textbooks), and dynamically generates interview
questions — rather than using a fixed question bank.

## Table of Contents
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Key Design Decisions](#key-design-decisions)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [API Overview](#api-overview)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Deployment](#deployment)

## Architecture

```
User → React Dashboard (Vite) → FastAPI Backend
                                    ├── API layer (validation, routing)
                                    ├── Service layer (business logic)
                                    │     ├── Resume Parser
                                    │     ├── Retrieval Service (RAG)
                                    │     ├── Question Generation Service
                                    │     └── Session Service (orchestration)
                                    ├── LLM Client → Groq API
                                    ├── Embedding Client → local sentence-transformers
                                    ├── Vector Store → ChromaDB (per-role collections)
                                    └── Data Layer → SQLAlchemy → Postgres/SQLite
```

**Layer responsibilities:**
- **API layer** (`app/api/`): thin routers — Pydantic validation + delegation only.
- **Service layer** (`app/services/`): all real logic (RAG orchestration, resume
  parsing, session lifecycle). This is the layer to read first to understand
  the system.
- **Data layer** (`app/db/`): SQLAlchemy models + repository functions,
  isolating raw queries from services.

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | React (Vite) + Tailwind | Fast dev loop, no SSR complexity needed for this single-user tool |
| Backend | FastAPI | Async, automatic OpenAPI docs, Pydantic validation |
| LLM | Groq API (Llama 3.3) | Free tier, fast inference, no payment method required |
| Embeddings | sentence-transformers (local, `all-MiniLM-L6-v2`) | Free, small enough to run on a free-tier host, no API key |
| Vector Store | ChromaDB (persistent, rebuilt at startup) | Zero external infra; rebuild-on-boot avoids ephemeral-disk data loss on free hosts |
| Relational DB | Postgres (Neon/Supabase free tier) via SQLAlchemy | Durable across redeploys — required since this is hosted |
| Resume Parsing | pypdf + rule-based skill matching | Deterministic, explainable, no heavy NLP dependency |

## Key Design Decisions

1. **Provider-agnostic LLM client** (`app/llm/client.py`): all Groq-specific
   code lives in one file. Swapping to OpenAI/Anthropic later is a one-file
   change.

2. **Token-aware chunking with overlap** (`ingestion/ingest_knowledge_base.py`):
   chunks are sized in tokens (via `tiktoken`), not raw characters, so chunk
   boundaries respect how the LLM actually consumes text. ~300 tokens per
   chunk with 50 tokens of overlap preserves cross-boundary context (a
   definition and its explanation rarely get split) while staying precise
   enough for retrieval.

3. **Traceability**: every generated question stores the `source_chunk_ids`
   that produced it. The summary view can show exactly which knowledge-base
   passages grounded each question — directly satisfying the assignment's
   traceability requirement.

4. **Knowledge base rebuilt at startup, not just once**: free hosting tiers
   often use ephemeral disks. Since the knowledge base is static (fixed
   textbook PDFs shipped in the repo), the app checks-and-rebuilds any
   missing ChromaDB collection on every boot — cheap, and removes any
   dependency on durable disk for KB data. Only actual interview data
   (sessions/Q&A) needs durable storage, which is why that lives in Postgres.

5. **Rule-based resume skill extraction**, not NLP/NER: deterministic, fast,
   fully explainable, and appropriate for the project's scope. Documented
   here as a clear upgrade path if more nuance is needed later.

6. **4 roles, each mapped to an actual provided textbook** (see
   `app/roles.py`): the assignment explicitly requires using the provided
   books, not generic internet content, as the RAG source — role definitions
   were chosen to match exactly what source material is available.

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- A free [Groq API key](https://console.groq.com/keys)
- (For hosting) A free Postgres instance from [Neon](https://neon.tech) or [Supabase](https://supabase.com)

### 1. Knowledge base files
Place the provided textbook PDFs in `backend/data/knowledge_base/` using the
filenames referenced in `backend/app/roles.py` (e.g.
`machine_learning_tom_mitchell.pdf`). Rename downloaded PDFs to match, or
edit `roles.py` to match your filenames.

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: add your GROQ_API_KEY

# One-time (or let it auto-run on first app startup):
python ingestion/ingest_knowledge_base.py

uvicorn app.main:app --reload
```
Backend runs at `http://localhost:8000`. Interactive API docs at
`http://localhost:8000/docs`.

### 3. Frontend
```bash
cd frontend
npm install
cp .env.example .env   # defaults to http://localhost:8000, adjust if needed
npm run dev
```
Frontend runs at `http://localhost:5173`.

## Environment Variables

**Backend (`backend/.env`):**
| Variable | Description |
|---|---|
| `DATABASE_URL` | `sqlite:///./data/app.db` locally, or a Postgres URL when hosted |
| `GROQ_API_KEY` | Your Groq API key |
| `LLM_MODEL` | Groq model name (default: `llama-3.3-70b-versatile`) |
| `EMBEDDING_MODEL` | sentence-transformers model name |
| `CHROMA_PERSIST_DIR` | Local path for the vector store |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `QUESTIONS_PER_INTERVIEW` | Number of questions per session (default 6) |
| `RETRIEVAL_TOP_K` | Chunks retrieved per question (default 4) |

**Frontend (`frontend/.env`):**
| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Backend base URL |

## API Overview

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/roles` | GET | List supported roles |
| `/api/sessions` | POST | Create session (upload resume + role) |
| `/api/sessions` | GET | List past sessions |
| `/api/sessions/{id}/next-question` | GET | Generate/return the next question |
| `/api/sessions/{id}/answers` | POST | Submit an answer |
| `/api/sessions/{id}/complete` | POST | Mark interview complete |
| `/api/sessions/{id}/summary` | GET | Full transcript + insights |

Full request/response schemas are available at `/docs` (Swagger UI) once the
backend is running.

## Database Schema

- **sessions**: one row per interview (role, resume filename, extracted
  skills, status)
- **questions**: one row per generated question (belongs to a session,
  stores `source_chunk_ids` for traceability)
- **answers**: one row per submitted answer (1:1 with a question)

## Testing

```bash
cd backend
pip install pytest
pytest tests/
```
Covers resume skill extraction and the chunking strategy — the two most
evaluation-critical, pure-logic components.

## Deployment

- **Frontend**: Vercel or Netlify (zero-config for Vite)
- **Backend**: Render or Railway (free tier); set all backend env vars in
  the platform's dashboard, not committed to the repo
- **Database**: Neon or Supabase (free Postgres tier)
- On backend boot, the app auto-creates DB tables and rebuilds the vector
  store if missing — no manual migration step needed for this project's scope

## Feature List
- Resume upload (PDF) with rule-based skill extraction
- Role selection across 4 roles, each grounded in a real provided textbook
- Full RAG pipeline: chunking → embedding → retrieval → grounded generation
- Sequential interview flow with progress tracking
- Full traceability from question → source knowledge-base chunk
- Session persistence and history (dashboard "Past Sessions" view)
- Structured summary with topics covered and skills touched
