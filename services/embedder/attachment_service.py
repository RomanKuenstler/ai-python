from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from services.common.config import Settings
from services.embedder.processors.processor_registry import ProcessorRegistry


@dataclass(slots=True)
class AttachmentJobFile:
    file_name: str
    content_base64: str


class AttachmentProcessingService:
    def __init__(self, *, settings: Settings, data_dir: Path) -> None:
        self.settings = settings
        self.registry = ProcessorRegistry(settings=settings, data_dir=data_dir)

    def process_files(self, files: list[AttachmentJobFile]) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        with TemporaryDirectory(prefix="attachment-job-") as temp_dir:
            temp_root = Path(temp_dir)
            for file in files:
                temp_path = temp_root / Path(file.file_name).name
                temp_path.write_bytes(base64.b64decode(file.content_base64))
                processor = self.registry.for_path(temp_path)
                extraction = processor.process(file_path=temp_path, relative_path=temp_path.name, tags=["attachment"])
                results.append(
                    {
                        "file_name": temp_path.name,
                        "content": extraction.text,
                        "type": temp_path.suffix.lower().lstrip(".") or "unknown",
                        "extraction_method": extraction.metadata.get("extraction_method"),
                        "quality": extraction.quality.to_metadata(),
                    }
                )
        return results
