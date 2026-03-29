from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from services.common.config import Settings
from services.embedder.utils import compute_text_sha256


@dataclass(slots=True)
class ExtractionQuality:
    is_useful: bool
    score: float
    char_count: int
    printable_ratio: float
    alphabetic_ratio: float
    average_word_length: float
    broken_fragment_ratio: float
    flags: list[str] = field(default_factory=list)

    def to_metadata(self) -> dict:
        return {
            "is_useful": self.is_useful,
            "score": self.score,
            "char_count": self.char_count,
            "printable_ratio": self.printable_ratio,
            "alphabetic_ratio": self.alphabetic_ratio,
            "average_word_length": self.average_word_length,
            "broken_fragment_ratio": self.broken_fragment_ratio,
            "flags": list(self.flags),
        }


@dataclass(slots=True)
class SemanticBlock:
    text: str
    title: str | None = None
    chapter: str | None = None
    section: str | None = None
    heading_path: list[str] = field(default_factory=list)
    page_number: int | None = None
    extraction_method: str | None = None
    content_type: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class ExtractionResult:
    text: str
    document_title: str | None
    sections: list[dict]
    metadata: dict
    quality: ExtractionQuality
    processing_flags: dict
    semantic_blocks: list[SemanticBlock] = field(default_factory=list)

    @classmethod
    def empty(
        cls,
        *,
        file_path: Path,
        extension: str,
        content_type: str,
        tags: list[str],
        quality: ExtractionQuality,
        reason: str,
        settings: Settings,
    ) -> "ExtractionResult":
        return cls(
            text="",
            document_title=None,
            sections=[],
            metadata={
                "file_name": file_path.name,
                "file_path": str(file_path),
                "extension": extension,
                "content_type": content_type,
                "tags": tags,
                "schema_version": settings.index_schema_version,
                "processor_version": settings.processor_version,
                "normalization_version": settings.normalization_version,
                "extraction_strategy_version": settings.extraction_strategy_version,
                "content_hash": "",
            },
            quality=quality,
            processing_flags={
                "processing_status": "no_useful_text",
                "processing_error": reason,
                "ocr_used": False,
            },
            semantic_blocks=[],
        )


class BaseProcessor:
    processor_name = "base"
    content_type = "text/plain"

    def __init__(self, *, settings: Settings, data_dir: Path) -> None:
        self.settings = settings
        self.data_dir = data_dir

    def process(self, *, file_path: Path, relative_path: str, tags: list[str]) -> ExtractionResult:
        raise NotImplementedError

    def build_base_metadata(self, *, file_path: Path, relative_path: str, tags: list[str]) -> dict:
        return {
            "file_name": file_path.name,
            "file_path": relative_path,
            "extension": file_path.suffix.lower(),
            "content_type": self.content_type,
            "tags": tags,
            "schema_version": self.settings.index_schema_version,
            "processor_version": self.settings.processor_version,
            "normalization_version": self.settings.normalization_version,
            "extraction_strategy_version": self.settings.extraction_strategy_version,
        }

    def finalize_result(
        self,
        *,
        file_path: Path,
        relative_path: str,
        tags: list[str],
        document_title: str | None,
        text: str,
        sections: list[dict],
        quality: ExtractionQuality,
        semantic_blocks: list[SemanticBlock],
        metadata: dict | None = None,
        processing_flags: dict | None = None,
    ) -> ExtractionResult:
        base_metadata = self.build_base_metadata(file_path=file_path, relative_path=relative_path, tags=tags)
        if metadata:
            base_metadata.update(metadata)
        base_metadata["document_title"] = document_title
        base_metadata["content_hash"] = compute_text_sha256(text) if text else ""
        return ExtractionResult(
            text=text,
            document_title=document_title,
            sections=sections,
            metadata=base_metadata,
            quality=quality,
            processing_flags=processing_flags or {"processing_status": "processed", "ocr_used": False},
            semantic_blocks=semantic_blocks,
        )
