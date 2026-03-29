from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from services.common.config import get_settings
from services.retriever.services.retriever_service import RetrieverAppService, build_retriever_app_service


@lru_cache(maxsize=1)
def get_retriever_service() -> RetrieverAppService:
    settings = get_settings()
    prompts_dir = Path(__file__).resolve().parents[3] / "prompts"
    return build_retriever_app_service(
        database_url=settings.database_url,
        embedding_model=settings.embedding_model,
        embedding_base_url=settings.embedding_base_url,
        embedding_api_key=settings.embedding_api_key,
        qdrant_url=settings.qdrant_url,
        qdrant_collection=settings.qdrant_collection,
        retrieval_score_threshold=settings.retrieval_score_threshold,
        retrieval_min_results=settings.retrieval_min_results,
        retrieval_max_results=settings.retrieval_max_results,
        llm_model=settings.llm_model,
        llm_base_url=settings.llm_base_url,
        llm_api_key=settings.llm_api_key,
        prompts_dir=prompts_dir,
        history_limit=settings.history_limit,
    )
