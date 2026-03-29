from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from services.common.config import get_settings
from services.common.logging import configure_logging
from services.embedder.chunking import Chunker
from services.embedder.embedding import EmbeddingClient
from services.embedder.postgres_client import EmbedderPostgresClient
from services.embedder.processor import FileProcessor
from services.embedder.qdrant_client import EmbedderQdrantClient
from services.embedder.utils import load_tags
from services.embedder.watcher import PollingWatcher


def main() -> None:
    load_dotenv()
    settings = get_settings()
    configure_logging(settings.log_level)

    data_dir = Path(settings.data_dir)
    postgres_client = EmbedderPostgresClient(settings.database_url)
    postgres_client.initialize()

    processor = FileProcessor(
        data_dir=data_dir,
        chunker=Chunker(settings.chunk_size, settings.chunk_overlap),
        embedding_client=EmbeddingClient(
            model=settings.embedding_model,
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            max_input_tokens=settings.embedding_max_input_tokens,
        ),
        postgres_client=postgres_client,
        qdrant_client=EmbedderQdrantClient(settings.qdrant_url, settings.qdrant_collection),
        tags_map=load_tags(data_dir / "tags.json"),
        settings=settings,
    )
    watcher = PollingWatcher(
        data_dir=data_dir,
        interval_seconds=settings.watch_interval,
        processor=processor,
        settings=settings,
    )
    watcher.sync_once()
    watcher.run()


if __name__ == "__main__":
    main()
