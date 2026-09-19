"""
Centralized configuration.

Why: every credential and environment-dependent value (DB URL, API keys,
model names) is read from environment variables via pydantic-settings.
Nothing is hardcoded, so the exact same code runs locally (SQLite) and
in production (Postgres) just by changing .env / host env vars.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/app.db"

    # LLM (Groq)
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"

    # Embeddings (local sentence-transformers)
    embedding_model: str = "all-MiniLM-L6-v2"

    # Vector store
    chroma_persist_dir: str = "./data/chroma_store"

    # App behavior
    cors_origins: str = "http://localhost:5173"
    questions_per_interview: int = 6
    retrieval_top_k: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    # lru_cache => settings are parsed once and reused (cheap, and avoids
    # re-reading .env on every request).
    return Settings()
