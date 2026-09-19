"""
FastAPI application entrypoint.

Keeps this file minimal: app creation, middleware, router registration,
and startup hooks only. All real logic lives in services/.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.session import Base, engine
from app.api import roles, sessions, interview
from app.services.ingestion_runner import run_startup_ingestion

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist yet (simple approach appropriate
    # for this project's scope; a migration tool like Alembic would be
    # the next step for a longer-lived production system).
    Base.metadata.create_all(bind=engine)
    run_startup_ingestion()
    yield


app = FastAPI(
    title="AI Interview Screening System",
    description="RAG-powered role-based candidate screening system.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roles.router)
app.include_router(sessions.router)
app.include_router(interview.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
