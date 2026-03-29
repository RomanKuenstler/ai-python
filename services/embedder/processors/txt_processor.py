from __future__ import annotations

from services.embedder.processors.base_processor import BaseProcessor, ExtractionResult, SemanticBlock
from services.embedder.processors.extraction_quality import evaluate_text_quality
from services.embedder.processors.shared_normalization import normalize_block_text


class TxtProcessor(BaseProcessor):
    processor_name = "txt"
    content_type = "text/plain"

    def process(self, *, file_path, relative_path: str, tags: list[str]) -> ExtractionResult:
        text = normalize_block_text(file_path.read_text(encoding="utf-8", errors="ignore"))
        quality = evaluate_text_quality(text)
        if not quality.is_useful:
            return ExtractionResult.empty(
                file_path=file_path,
                extension=file_path.suffix.lower(),
                content_type=self.content_type,
                tags=tags,
                quality=quality,
                reason="txt_extraction_not_useful",
                settings=self.settings,
            )
        blocks = [SemanticBlock(text=paragraph, content_type=self.content_type) for paragraph in text.split("\n\n") if paragraph.strip()]
        return self.finalize_result(
            file_path=file_path,
            relative_path=relative_path,
            tags=tags,
            document_title=file_path.stem,
            text=text,
            sections=[],
            quality=quality,
            semantic_blocks=blocks,
            metadata={"extraction_method": "plain_text"},
        )
