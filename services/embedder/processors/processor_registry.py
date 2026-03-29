from __future__ import annotations

from pathlib import Path

from services.common.config import Settings
from services.embedder.processors.base_processor import BaseProcessor
from services.embedder.processors.epub_processor import EpubProcessor
from services.embedder.processors.html_processor import HtmlProcessor
from services.embedder.processors.markdown_processor import MarkdownProcessor
from services.embedder.processors.pdf_processor import PdfProcessor
from services.embedder.processors.txt_processor import TxtProcessor


class ProcessorRegistry:
    def __init__(self, *, settings: Settings, data_dir: Path) -> None:
        shared = {"settings": settings, "data_dir": data_dir}
        self._processors: dict[str, BaseProcessor] = {
            ".txt": TxtProcessor(**shared),
            ".md": MarkdownProcessor(**shared),
            ".html": HtmlProcessor(**shared),
            ".htm": HtmlProcessor(**shared),
            ".pdf": PdfProcessor(**shared),
            ".epub": EpubProcessor(**shared),
        }

    def for_path(self, file_path: Path) -> BaseProcessor:
        try:
            return self._processors[file_path.suffix.lower()]
        except KeyError as exc:
            raise ValueError(f"Unsupported file type: {file_path.suffix}") from exc
