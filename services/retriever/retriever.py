from __future__ import annotations

from collections.abc import Callable
from typing import Any

from services.common.qdrant import QdrantStore
from services.embedder.embedding import EmbeddingClient


class RetrievalService:
    def __init__(
        self,
        *,
        embedding_client: EmbeddingClient,
        qdrant_store: QdrantStore,
        score_threshold: float,
        min_results: int,
        max_results: int,
        candidate_filter: Callable[[list[dict[str, Any]], int, str | None, bool, dict[str, Any] | None], list[dict[str, Any]]] | None = None,
    ) -> None:
        self.embedding_client = embedding_client
        self.qdrant_store = qdrant_store
        self.score_threshold = score_threshold
        self.min_results = min_results
        self.max_results = max_results
        self.candidate_filter = candidate_filter

    def retrieve(
        self,
        query: str,
        *,
        user_id: int = 0,
        chat_id: str | None = None,
        is_admin: bool = False,
        gpt_overrides: dict[str, Any] | None = None,
        min_results: int | None = None,
        max_results: int | None = None,
        score_threshold: float | None = None,
    ) -> list[dict[str, str | float | list[str]]]:
        resolved_min = min_results if min_results is not None else self.min_results
        resolved_max = max_results if max_results is not None else self.max_results
        resolved_threshold = score_threshold if score_threshold is not None else self.score_threshold
        query_vector = self.embedding_client.embed_query(query)
        candidates = self.qdrant_store.search(query_vector=query_vector, limit=resolved_max * 3)
        if self.candidate_filter is not None:
            try:
                candidates = self.candidate_filter(
                    candidates,
                    user_id=user_id,
                    chat_id=chat_id,
                    is_admin=is_admin,
                    gpt_overrides=gpt_overrides,
                )
            except TypeError:
                try:
                    candidates = self.candidate_filter(candidates, user_id, chat_id, is_admin, gpt_overrides)
                except TypeError:
                    candidates = self.candidate_filter(candidates, user_id, chat_id, is_admin)
        accepted = [candidate for candidate in candidates if float(candidate["score"]) >= resolved_threshold]
        accepted.sort(key=lambda candidate: float(candidate["score"]), reverse=True)
        if len(accepted) < resolved_min:
            return accepted
        return accepted[:resolved_max]
