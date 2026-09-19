"""
Database engine + session factory.

Why a separate module: keeps engine creation in one place so both the
app (via get_db dependency) and one-off scripts (e.g. ingestion, tests)
can reuse the exact same configured engine without duplicating connection
logic.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import get_settings

settings = get_settings()

# SQLite needs this connect_arg when used from multiple threads (FastAPI
# runs endpoint handlers in a threadpool for sync code). Postgres ignores
# the extra kwarg being absent since we only pass it conditionally.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and guarantees it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
