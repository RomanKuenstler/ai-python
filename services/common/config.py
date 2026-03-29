from __future__ import annotations

import os
from dataclasses import dataclass


def _get_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _get_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


@dataclass(slots=True)
class Settings:
    postgres_db: str = os.getenv("POSTGRES_DB", "rag")
    postgres_user: str = os.getenv("POSTGRES_USER", "rag")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "rag")
    postgres_host: str = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port: int = _get_int("POSTGRES_PORT", 5432)
    qdrant_url: str = os.getenv("QDRANT_URL", "http://qdrant:6333")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "rag_chunks")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
    embedding_base_url: str = os.getenv("EMBEDDING_BASE_URL", "http://host.docker.internal:11434/v1")
    embedding_api_key: str = os.getenv("EMBEDDING_API_KEY", "dummy")
    llm_model: str = os.getenv("LLM_MODEL", "qwen3.5-4b")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://host.docker.internal:11434/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "dummy")
    chunk_size: int = _get_int("CHUNK_SIZE", 600)
    chunk_overlap: int = _get_int("CHUNK_OVERLAP", 100)
    watch_interval: int = _get_int("WATCH_INTERVAL", 10)
    retrieval_score_threshold: float = _get_float("RETRIEVAL_SCORE_THRESHOLD", 0.70)
    retrieval_min_results: int = _get_int("RETRIEVAL_MIN_RESULTS", 2)
    retrieval_max_results: int = _get_int("RETRIEVAL_MAX_RESULTS", 8)
    history_limit: int = _get_int("HISTORY_LIMIT", 5)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    data_dir: str = os.getenv("DATA_DIR", "/app/data")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def get_settings() -> Settings:
    return Settings()
