from __future__ import annotations

from services.embedder.ocr import extract_text_from_image_bytes
from services.embedder.processors.base_processor import BaseProcessor, ExtractionResult, SemanticBlock
from services.embedder.processors.extraction_quality import evaluate_text_quality


class ImageProcessor(BaseProcessor):
    processor_name = "image"
    content_type = "image"

    def process(self, *, file_path, relative_path: str, tags: list[str]) -> ExtractionResult:
        if not self.settings.enable_attachment_ocr:
            return ExtractionResult.empty(
                file_path=file_path,
                extension=file_path.suffix.lower(),
                content_type=self.content_type,
                tags=tags,
                quality=evaluate_text_quality(""),
                reason="attachment_image_ocr_disabled",
                settings=self.settings,
            )

        text = extract_text_from_image_bytes(file_path.read_bytes(), self.settings)
        quality = evaluate_text_quality(text)
        if not quality.is_useful:
            return ExtractionResult.empty(
                file_path=file_path,
                extension=file_path.suffix.lower(),
                content_type=self.content_type,
                tags=tags,
                quality=quality,
                reason="image_ocr_not_useful",
                settings=self.settings,
            )

        block = SemanticBlock(
            text=text,
            title=file_path.stem,
            section=file_path.stem,
            extraction_method="ocr",
            content_type=self.content_type,
        )
        return self.finalize_result(
            file_path=file_path,
            relative_path=relative_path,
            tags=tags,
            document_title=file_path.stem,
            text=text,
            sections=[{"title": file_path.stem, "section": file_path.stem}],
            quality=quality,
            semantic_blocks=[block],
            metadata={"extraction_method": "ocr"},
            processing_flags={
                "processing_status": "processed",
                "processing_error": None,
                "ocr_used": True,
            },
        )
