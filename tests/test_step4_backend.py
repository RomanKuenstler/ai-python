from __future__ import annotations

from services.embedder.utils import normalize_tags
from services.retriever.retriever import RetrievalService


class StubEmbeddingClient:
    def embed_query(self, query: str) -> list[float]:
        return [0.1, 0.2]


class StubQdrantStore:
    def search(self, query_vector: list[float], limit: int):
        return [
            {"file_path": "enabled.md", "score": 0.9, "file_name": "enabled.md", "chunk_id": "1", "text": "enabled"},
            {"file_path": "disabled.md", "score": 0.88, "file_name": "disabled.md", "chunk_id": "2", "text": "disabled"},
        ]


def test_normalize_tags_defaults_and_deduplicates() -> None:
    assert normalize_tags([" docker ", "", "Docker", "docs"], "default") == ["docker", "docs"]
    assert normalize_tags([], "default") == ["default"]


def test_retrieval_service_filters_disabled_files() -> None:
    service = RetrievalService(
        embedding_client=StubEmbeddingClient(),
        qdrant_store=StubQdrantStore(),
        score_threshold=0.5,
        min_results=1,
        max_results=5,
        candidate_filter=lambda candidates, _user_id, _chat_id, _is_admin: [
            candidate for candidate in candidates if candidate["file_path"] == "enabled.md"
        ],
    )

    results = service.retrieve("hello")

    assert len(results) == 1
    assert results[0]["file_path"] == "enabled.md"
