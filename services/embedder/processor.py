from __future__ import annotations

import logging
from pathlib import Path

from services.embedder.chunking import Chunker
from services.embedder.embedding import EmbeddingClient
from services.embedder.postgres_client import EmbedderPostgresClient
from services.embedder.qdrant_client import EmbedderQdrantClient
from services.embedder.utils import compute_sha256, normalize_text

LOGGER = logging.getLogger(__name__)


class FileProcessor:
    def __init__(
        self,
        *,
        data_dir: Path,
        chunker: Chunker,
        embedding_client: EmbeddingClient,
        postgres_client: EmbedderPostgresClient,
        qdrant_client: EmbedderQdrantClient,
        tags_map: dict[str, list[str]],
    ) -> None:
        self.data_dir = data_dir
        self.chunker = chunker
        self.embedding_client = embedding_client
        self.postgres_client = postgres_client
        self.qdrant_client = qdrant_client
        self.tags_map = tags_map

    def process(self, file_path: Path) -> None:
        file_hash = compute_sha256(file_path)
        relative_path = str(file_path.relative_to(self.data_dir))
        normalized = normalize_text(file_path.read_text(encoding="utf-8", errors="ignore"))
        chunks = self.chunker.split(file_path, normalized)
        resolved_tags = self.resolve_tags(relative_path, file_path.name)
        tagged_chunks = [{"chunk_id": f"{relative_path}:{index}", "text": chunk, "tags": resolved_tags} for index, chunk in enumerate(chunks)]
        embeddings = self.embedding_client.embed_documents([chunk["text"] for chunk in tagged_chunks]) if tagged_chunks else []

        if tagged_chunks:
            self.qdrant_client.sync_file(
                file_name=file_path.name,
                file_path=relative_path,
                file_hash=file_hash,
                tags=resolved_tags,
                chunks=tagged_chunks,
                embeddings=embeddings,
            )
        else:
            self.qdrant_client.delete_file(relative_path)
        self.postgres_client.upsert_file_with_chunks(
            file_path=relative_path,
            file_name=file_path.name,
            file_hash=file_hash,
            tags=resolved_tags,
            chunks=tagged_chunks,
        )
        LOGGER.info("Processed file", extra={"file_path": relative_path, "chunks": len(tagged_chunks)})

    def delete(self, relative_path: str) -> None:
        self.qdrant_client.delete_file(relative_path)
        self.postgres_client.delete_file(relative_path)
        LOGGER.info("Deleted file state", extra={"file_path": relative_path})

    def resolve_tags(self, relative_path: str, file_name: str) -> list[str]:
        return self.tags_map.get(relative_path, self.tags_map.get(file_name, []))
