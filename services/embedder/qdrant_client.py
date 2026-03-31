from __future__ import annotations

from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

from qdrant_client.http import models

from services.common.qdrant import QdrantStore


class EmbedderQdrantClient:
    def __init__(self, url: str, collection_name: str) -> None:
        self.store = QdrantStore(url=url, collection_name=collection_name)

    def sync_file(
        self,
        *,
        file_name: str,
        file_path: str,
        file_hash: str,
        tags: list[str],
        chunks: list[dict[str, str | list[str]]],
        embeddings: list[list[float]],
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        points = []
        for chunk, vector in zip(chunks, embeddings, strict=True):
            payload = {
                "file_name": file_name,
                "file_path": file_path,
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "title": chunk.get("title"),
                "chapter": chunk.get("chapter"),
                "section": chunk.get("section"),
                "heading_path": chunk.get("heading_path", []),
                "page_number": chunk.get("page_number"),
                "extraction_method": chunk.get("extraction_method"),
                "content_type": chunk.get("content_type"),
                "quality_flags": chunk.get("quality_flags", []),
                "tags": tags,
                "hash": file_hash,
                "content_hash": chunk.get("metadata", {}).get("normalized_content_hash", ""),
                "document_title": chunk.get("metadata", {}).get("document_title", ""),
                "author": chunk.get("metadata", {}).get("author", ""),
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            points.append(
                models.PointStruct(
                    id=str(uuid5(NAMESPACE_URL, str(chunk["chunk_id"]))),
                    vector=vector,
                    payload=payload,
                )
            )

        vector_size = len(embeddings[0]) if embeddings else 0
        self.store.replace_file_points(file_path=file_path, points=points, vector_size=vector_size)

    def delete_file(self, file_path: str) -> None:
        self.store.delete_file_points(file_path)
