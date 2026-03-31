from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import Depends, Header, HTTPException, Response

from services.common.config import get_settings
from services.retriever.auth import AuthContext
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
        embedding_max_input_tokens=settings.embedding_max_input_tokens,
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
        settings=settings,
    )


def get_auth_context(
    response: Response,
    authorization: str | None = Header(default=None),
    service: RetrieverAppService = Depends(get_retriever_service),
) -> AuthContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization[7:].strip()
    try:
        auth = service.auth_manager.authenticate_token(token)
    except PermissionError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    if auth.refreshed_token:
        response.headers["X-Auth-Token"] = auth.refreshed_token
        response.headers["X-Auth-Expires-At"] = auth.session.expires_at.isoformat()
        response.headers["X-Auth-Max-Expires-At"] = auth.session.max_expires_at.isoformat()
    return auth


def get_app_auth_context(auth: AuthContext = Depends(get_auth_context)) -> AuthContext:
    if auth.user.force_password_change:
        raise HTTPException(status_code=403, detail="Password change required")
    return auth
