# IntelliScreen — AI-Powered Role-Based Candidate Screening

> **A RAG-powered technical interview system that generates candidate-specific interview questions grounded in role-specific knowledge sources.**

IntelliScreen is an AI-powered candidate screening platform designed to simulate a structured technical interview.

Instead of relying on a static question bank, IntelliScreen analyzes a candidate's resume, identifies relevant skills and technologies, retrieves context from role-specific machine learning and AI textbooks, and uses that context to dynamically generate interview questions.

Every generated question maintains **source traceability**, allowing the system to identify the exact knowledge-base chunks used to generate it.

---

## 🚀 Demo

> 🎥 **Demo Video:** https://drive.google.com/drive/home?dmr=1&ec=wgc-drive-%5Bmodule%5D-goto**



---

## ✨ Features

### 📄 Resume Analysis

* Upload candidate resumes in PDF format
* Extract text using `pypdf`
* Detect relevant skills and technologies using deterministic rule-based matching
* Store extracted candidate information with the interview session

### 🎯 Role-Based Screening

Candidates can select from multiple technical roles.

Each role is associated with a dedicated knowledge base built from provided ML/AI textbooks rather than generic internet content.

### 🧠 Retrieval-Augmented Generation

IntelliScreen implements a complete RAG pipeline:

```text
Textbook PDFs
     ↓
Text Extraction
     ↓
Token-Aware Chunking
     ↓
Embedding Generation
     ↓
ChromaDB Vector Store
     ↓
Semantic Retrieval
     ↓
Candidate + Role Context
     ↓
LLM
     ↓
Grounded Interview Question
```

### 🔎 Source Traceability

Every generated question stores the IDs of the knowledge-base chunks used during retrieval.

This makes it possible to trace:

```text
Interview Question
       ↓
Retrieved Chunk
       ↓
Source Passage
       ↓
Original Textbook
```

This provides greater transparency compared with a conventional LLM-only interview generator.

### 💬 Structured Interview Flow

* Sequential interview questions
* Live interview progress
* Answer submission
* Session persistence
* Interview completion tracking

### 📊 Interview Summary

After the interview, the system provides:

* Complete transcript
* Questions asked
* Candidate answers
* Topics covered
* Candidate skills touched during the interview
* Session information

### 🗂️ Session History

Previous interviews are persisted and accessible through the dashboard.

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      Candidate       │
                         │    Resume + Role     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    React Dashboard   │
                         │    Vite + Tailwind   │
                         └──────────┬───────────┘
                                    │ REST API
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │      API Layer       │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
        ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
        │ Resume Parser  │  │ Session        │  │ RAG Retrieval  │
        │                │  │ Service        │  │ Service        │
        └────────────────┘  └────────────────┘  └───────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │    ChromaDB     │
                                                │ Vector Database  │
                                                └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │ Retrieved Context│
                                                └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │    Groq LLM     │
                                                │  GPT-OSS-20B    │
                                                └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │ Interview       │
                                                │ Question        │
                                                └─────────────────┘
```

---

# 🧠 RAG Pipeline

The core of IntelliScreen is its retrieval-augmented generation pipeline.

## 1. Knowledge Base Ingestion

Provided textbook PDFs are processed during ingestion.

```text
PDF
 ↓
Text Extraction
 ↓
Token-Aware Chunking
 ↓
Embedding Generation
 ↓
ChromaDB
```

The system uses approximately **300-token chunks with 50-token overlap**.

Token-based chunking is used instead of character-based chunking so that the resulting context better matches the way the LLM consumes tokens.

---

## 2. Semantic Retrieval

When a question needs to be generated, IntelliScreen retrieves the most relevant knowledge-base chunks based on the candidate's selected role and interview context.

Default configuration:

```text
Top-K Retrieved Chunks: 4
```

---

## 3. Candidate Context

The retrieved textbook context is combined with information extracted from the candidate's resume.

For example:

```text
Candidate Skills:
Python
Machine Learning
XGBoost
FastAPI

Selected Role:
Machine Learning Engineer

Retrieved Knowledge:
Supervised Learning
Model Evaluation
Classification
Feature Engineering
```

The combined context is provided to the LLM.

---

## 4. Grounded Question Generation

The LLM generates an interview question using the retrieved context.

The generated question is stored together with:

```text
question
source_chunk_ids
session_id
```

This provides end-to-end traceability.

---

# 🛠️ Tech Stack

| Layer               | Technology            |
| ------------------- | --------------------- |
| Frontend            | React + Vite          |
| Styling             | Tailwind CSS          |
| Backend             | FastAPI               |
| Language            | Python                |
| LLM                 | Groq API              |
| LLM Model           | `openai/gpt-oss-20b`  |
| Embeddings          | Sentence Transformers |
| Embedding Model     | `all-MiniLM-L6-v2`    |
| Vector Database     | ChromaDB              |
| Relational Database | SQLite / PostgreSQL   |
| ORM                 | SQLAlchemy            |
| Resume Parsing      | pypdf                 |
| Validation          | Pydantic              |
| Testing             | Pytest                |

---

# 🧩 Project Structure

```text
IntelliScreen/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   ├── roles.py
│   │   │   └── sessions.py
│   │   │
│   │   ├── services/
│   │   │   ├── resume_parser.py
│   │   │   ├── retrieval_service.py
│   │   │   ├── question_service.py
│   │   │   └── session_service.py
│   │   │
│   │   ├── db/
│   │   │   ├── models.py
│   │   │   └── repository.py
│   │   │
│   │   ├── llm/
│   │   │   └── client.py
│   │   │
│   │   ├── roles.py
│   │   └── main.py
│   │
│   ├── ingestion/
│   │   └── ingest_knowledge_base.py
│   │
│   ├── tests/
│   │
│   ├── data/
│   │   └── knowledge_base/
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── pages/
│   │   └── services/
│   │
│   ├── package.json
│   └── .env.example
│
└── README.md
```

---

# 🔑 Key Engineering Decisions

## Provider-Agnostic LLM Layer

Groq-specific logic is isolated inside:

```text
app/llm/client.py
```

This allows the LLM provider to be replaced without modifying the rest of the application architecture.

---

## Token-Aware Chunking

Knowledge-base documents are chunked using tokens rather than raw character counts.

Configuration:

```text
Chunk Size:  ~300 tokens
Overlap:      ~50 tokens
```

The overlap helps preserve context across chunk boundaries.

---

## Explainable Resume Extraction

Instead of introducing a heavy NLP/NER pipeline, IntelliScreen uses deterministic rule-based skill matching.

Advantages:

* Fast
* Lightweight
* Easy to debug
* Explainable
* No additional model inference required

This also provides a clear path for future improvements using NLP-based entity extraction.

---

## Persistent Interview Data

Interview sessions are stored using SQLAlchemy.

The application supports:

```text
SQLite
   ↓
Local development

PostgreSQL
   ↓
Production deployment
```

The database can be switched through:

```env
DATABASE_URL=...
```

without changing application logic.

---

## Resilient Knowledge Base

The vector database can be rebuilt automatically when required.

This is particularly useful for deployments using ephemeral storage because the knowledge base can be regenerated from the static textbook files during startup.

---

# 📚 Knowledge Base

The system is designed around provided ML/AI textbooks, including:

```text
machine_learning_tom_mitchell.pdf
hundred_page_ml_book.pdf
ml_for_absolute_beginners.pdf
intro_to_ml_with_python.pdf
master_ml_algorithms_brownlee.pdf
ai_ml_deep_learning.pdf
pattern_recognition_bishop.pdf
```

These files should be placed inside:

```text
backend/data/knowledge_base/
```

> **Note:** Make sure you have the appropriate rights to use and redistribute any textbook PDFs included with the repository. Do not commit copyrighted books unless redistribution is permitted.

---

# ⚙️ Getting Started

## Prerequisites

* Python 3.11+
* Node.js 18+
* Git
* Groq API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/intelliscreen.git

cd intelliscreen
```

---

# 2. Backend Setup

```bash
cd backend
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create environment file:

```bash
cp .env.example .env
```

For Windows, create `.env` manually if `cp` is unavailable.

Add your Groq API key:

```env
GROQ_API_KEY=your_api_key_here
```

---

# 3. Add Knowledge Base

Place the required textbook PDFs inside:

```text
backend/data/knowledge_base/
```

Then run ingestion:

```bash
python ingestion/ingest_knowledge_base.py
```

---

# 4. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

# 5. Frontend Setup

Open a new terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create:

```text
.env
```

Add:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

The application will be available at:

```text
http://localhost:5173
```

---

# 🔐 Environment Variables

## Backend

```env
DATABASE_URL=sqlite:///./data/app.db

GROQ_API_KEY=your_groq_api_key

LLM_MODEL=openai/gpt-oss-20b

EMBEDDING_MODEL=all-MiniLM-L6-v2

CHROMA_PERSIST_DIR=./data/chroma

CORS_ORIGINS=http://localhost:5173

QUESTIONS_PER_INTERVIEW=6

RETRIEVAL_TOP_K=4
```

## Frontend

```env
VITE_API_BASE_URL=http://localhost:8000
```

> Never commit `.env` files or API keys to GitHub.

---

# 🔌 API Endpoints

| Method | Endpoint                           | Description                   |
| ------ | ---------------------------------- | ----------------------------- |
| `GET`  | `/api/roles`                       | Get supported interview roles |
| `POST` | `/api/sessions`                    | Create an interview session   |
| `GET`  | `/api/sessions`                    | Retrieve previous sessions    |
| `GET`  | `/api/sessions/{id}/next-question` | Generate the next question    |
| `POST` | `/api/sessions/{id}/answers`       | Submit candidate answer       |
| `POST` | `/api/sessions/{id}/complete`      | Complete interview            |
| `GET`  | `/api/sessions/{id}/summary`       | Retrieve interview summary    |

Interactive API documentation is available through FastAPI Swagger:

```text
http://localhost:8000/docs
```

---

# 🗄️ Database Design

### Sessions

Stores:

```text
id
role
resume_filename
extracted_skills
status
created_at
```

### Questions

Stores:

```text
id
session_id
question
source_chunk_ids
created_at
```

### Answers

Stores:

```text
id
question_id
answer
created_at
```

Relationship:

```text
Session
   │
   ├── Question
   │      └── Answer
   │
   ├── Question
   │      └── Answer
   │
   └── Question
          └── Answer
```

---

# 🧪 Testing

Run the test suite:

```bash
cd backend

pytest tests/ -v
```

Current tests cover:

* Resume skill extraction
* Skill matching edge cases
* Token-aware chunking
* Chunk overlap behavior

---

# ✅ Manual Testing Checklist

Before deployment:

```text
☐ Upload different resumes for the same role
☐ Verify questions change based on candidate skills
☐ Complete a full interview
☐ Verify no questions are skipped
☐ Verify answers are stored
☐ Verify interview summary
☐ Verify source chunk IDs
☐ Restart backend and verify sessions persist
☐ Upload an invalid file and verify graceful error handling
```

---

# ⚠️ Known Limitations

### No Adaptive Follow-Up Questions

The current interview flow is sequential.

Future versions can analyze the candidate's previous answer and generate a deeper follow-up question.

### Rule-Based Resume Parsing

Skill extraction currently relies on deterministic matching rather than a dedicated NLP/NER model.

A future implementation could use:

* Named Entity Recognition
* LLM-based structured extraction
* Resume section classification
* Skill ontology matching

### No Authentication

The current implementation is designed primarily as a single-user evaluation/demo application.

Production deployment would require:

* Authentication
* Authorization
* User isolation
* Secure session management

### Database Migrations

The current implementation uses SQLAlchemy `create_all()` rather than Alembic migrations.

For a larger production system, migration management should be introduced.

### LLM Output Reliability

LLM responses can occasionally require retries or validation.

The client includes retry handling and response validation to reduce failures.

---

# 🔮 Future Improvements

Planned improvements include:

* [ ] Adaptive follow-up questions
* [ ] Authentication and user accounts
* [ ] Candidate scoring and structured evaluation
* [ ] Semantic resume parsing
* [ ] Interview difficulty adjustment
* [ ] Voice-based interviews
* [ ] Real-time interviewer dashboard
* [ ] Advanced candidate analytics
* [ ] Multi-tenant architecture
* [ ] Redis-based caching
* [ ] Production-grade observability
* [ ] Automated evaluation of generated questions
* [ ] Support for additional LLM providers

---

# ☁️ Deployment

A possible deployment architecture:

```text
                    ┌───────────────┐
                    │    Vercel     │
                    │ React Frontend│
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Render     │
                    │ FastAPI       │
                    └───────┬───────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       ┌─────────────┐             ┌─────────────┐
       │    Neon     │             │    Groq     │
       │  PostgreSQL │             │     LLM     │
       └─────────────┘             └─────────────┘
```

Suggested services:

* Frontend → Vercel / Netlify
* Backend → Render / Railway
* PostgreSQL → Neon / Supabase
* LLM → Groq
* Vector store → ChromaDB

---

# 🔒 Security Notes

Do not commit:

```text
.env
.env.local
API keys
database credentials
private resumes
copyrighted textbook PDFs
```

Recommended `.gitignore` entries:

```gitignore
.env
.env.*
!.env.example

venv/
__pycache__/
*.pyc

data/*.db
data/chroma/

node_modules/
dist/

*.pdf
```

---

# 💡 Why IntelliScreen?

Traditional interview platforms typically rely on predefined question banks.

IntelliScreen explores a different approach:

```text
Static Question Bank
        ↓
Same Questions
        ↓
Limited Candidate Context
```

versus:

```text
Candidate Resume
        +
Selected Role
        +
Retrieved Domain Knowledge
        ↓
Dynamic Question Generation
        ↓
Candidate-Specific Interview
        ↓
Source Traceability
```

The combination of **RAG + resume context + role-specific knowledge + source traceability** makes the system useful as an experimental framework for AI-assisted technical screening.

---

# 👩‍💻 Author

**Swastika Kumari**

B.Tech — Artificial Intelligence & Machine Learning

### Connect

* GitHub: [@swastikakumari9b44](https://github.com/swastikakumari9b44)
* LinkedIn: [Swastika Kumari](https://www.linkedin.com/in/swastika-kumari-3525b7403/)

---

## ⭐ If you found this project interesting

Feel free to explore the code, open an issue, or contribute improvements.

**Built with React, FastAPI, ChromaDB, Sentence Transformers, SQLAlchemy and Groq.**
