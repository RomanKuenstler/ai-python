from __future__ import annotations

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
    ) -> None:
        self.embedding_client = embedding_client
        self.qdrant_store = qdrant_store
        self.score_threshold = score_threshold
        self.min_results = min_results
        self.max_results = max_results

    def retrieve(self, query: str) -> list[dict[str, str | float | list[str]]]:
        query_vector = self.embedding_client.embed_query(query)
        candidates = self.qdrant_store.search(query_vector=query_vector, limit=self.max_results * 3)
        accepted = [candidate for candidate in candidates if float(candidate["score"]) >= self.score_threshold]
        accepted.sort(key=lambda candidate: float(candidate["score"]), reverse=True)
        if len(accepted) < self.min_results:
            return accepted
        return accepted[: self.max_results]
