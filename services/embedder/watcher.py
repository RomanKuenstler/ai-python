from __future__ import annotations

import logging
import time
from pathlib import Path

from services.common.config import Settings
from services.embedder.processor import FileProcessor
from services.embedder.utils import compute_sha256, load_tags

LOGGER = logging.getLogger(__name__)


SUPPORTED_EXTENSIONS = {".md", ".txt", ".html", ".htm", ".pdf", ".epub"}


class PollingWatcher:
    def __init__(self, *, data_dir: Path, interval_seconds: int, processor: FileProcessor, settings: Settings) -> None:
        self.data_dir = data_dir
        self.interval_seconds = interval_seconds
        self.processor = processor
        self.settings = settings

    def run(self) -> None:
        while True:
            self.processor.tags_map = load_tags(self.data_dir / "tags.json")
            self.sync_once()
            time.sleep(self.interval_seconds)

    def sync_once(self) -> None:
        disk_files = {
            str(path.relative_to(self.data_dir)): path
            for path in self.data_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        }
        tracked_files = {record.file_path: record for record in self.processor.postgres_client.list_files()}

        for relative_path, absolute_path in disk_files.items():
            file_hash = compute_sha256(absolute_path)
            tracked = tracked_files.get(relative_path)
            needs_reindex = tracked is None or tracked.file_hash != file_hash or self._settings_changed(tracked)
            if needs_reindex:
                reason = "new" if tracked is None else "content_or_settings_changed"
                LOGGER.info("Detected file change", extra={"file_path": relative_path, "reindex_reason": reason})
                self.processor.process(absolute_path)

        deleted_files = set(tracked_files) - set(disk_files)
        for relative_path in deleted_files:
            LOGGER.info("Detected file deletion", extra={"file_path": relative_path})
            self.processor.delete(relative_path)

    def _settings_changed(self, tracked) -> bool:
        return any(
            [
                tracked.chunk_size != self.settings.chunk_size,
                tracked.chunk_overlap != self.settings.chunk_overlap,
                tracked.index_schema_version != self.settings.index_schema_version,
                tracked.processor_version != self.settings.processor_version,
                tracked.normalization_version != self.settings.normalization_version,
                tracked.extraction_strategy_version != self.settings.extraction_strategy_version,
                tracked.processing_signature != self.settings.processing_signature,
            ]
        )
