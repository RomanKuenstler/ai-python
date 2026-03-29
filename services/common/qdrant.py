from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from services.common.retry import retry


class QdrantStore:
    """Stores cosine similarity as an internal score where higher is always better."""

    def __init__(self, url: str, collection_name: str) -> None:
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name

    def collection_exists(self) -> bool:
        return retry(lambda: self.client.collection_exists(self.collection_name))

    def ensure_collection(self, vector_size: int) -> None:
        def _ensure() -> None:
            if self.client.collection_exists(self.collection_name):
                return
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )

        retry(_ensure)

    def replace_file_points(self, file_path: str, points: list[models.PointStruct], vector_size: int) -> None:
        self.ensure_collection(vector_size)
        self.delete_file_points(file_path)
        if not points:
            return
        retry(lambda: self.client.upsert(collection_name=self.collection_name, points=points))

    def delete_file_points(self, file_path: str) -> None:
        if not self.collection_exists():
            return
        retry(
            lambda: self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[models.FieldCondition(key="file_path", match=models.MatchValue(value=file_path))]
                    )
                ),
            )
        )

    def search(self, query_vector: list[float], limit: int) -> list[dict[str, Any]]:
        if not self.collection_exists():
            return []

        results = retry(
            lambda: self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True,
            )
        )
        return [
            {
                "score": float(result.score),
                "file_name": result.payload.get("file_name", ""),
                "file_path": result.payload.get("file_path", ""),
                "chunk_id": result.payload.get("chunk_id", ""),
                "text": result.payload.get("text", ""),
                "tags": result.payload.get("tags", []),
                "hash": result.payload.get("hash", ""),
                "created_at": result.payload.get("created_at", ""),
                "updated_at": result.payload.get("updated_at", ""),
            }
            for result in results
        ]
