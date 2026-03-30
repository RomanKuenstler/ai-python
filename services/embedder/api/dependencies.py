from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from services.common.config import get_settings
from services.embedder.attachment_service import AttachmentProcessingService


@lru_cache(maxsize=1)
def get_attachment_processing_service() -> AttachmentProcessingService:
    settings = get_settings()
    return AttachmentProcessingService(settings=settings, data_dir=Path(settings.data_dir))
