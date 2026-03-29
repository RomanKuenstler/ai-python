from __future__ import annotations

from services.embedder.processors.base_processor import BaseProcessor, ExtractionResult, SemanticBlock
from services.embedder.processors.extraction_quality import evaluate_text_quality
from services.embedder.processors.shared_normalization import normalize_block_text


class MarkdownProcessor(BaseProcessor):
    processor_name = "markdown"
    content_type = "markdown"

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
                reason="markdown_extraction_not_useful",
                settings=self.settings,
            )
        heading_stack: list[str] = []
        blocks: list[SemanticBlock] = []
        first_heading: str | None = None
        for paragraph in [part for part in text.split("\n\n") if part.strip()]:
            first_line = paragraph.splitlines()[0]
            if first_line.startswith("#"):
                heading = first_line.lstrip("#").strip()
                level = len(first_line) - len(first_line.lstrip("#"))
                heading_stack = heading_stack[: max(level - 1, 0)]
                heading_stack.append(heading)
                if first_heading is None:
                    first_heading = heading
                blocks.append(
                    SemanticBlock(
                        text=paragraph,
                        title=heading,
                        chapter=heading_stack[0] if heading_stack else None,
                        section=heading,
                        heading_path=list(heading_stack),
                        content_type=self.content_type,
                    )
                )
            else:
                blocks.append(
                    SemanticBlock(
                        text=paragraph,
                        title=heading_stack[-1] if heading_stack else file_path.stem,
                        chapter=heading_stack[0] if heading_stack else None,
                        section=heading_stack[-1] if heading_stack else None,
                        heading_path=list(heading_stack),
                        content_type=self.content_type,
                    )
                )
        document_title = first_heading or file_path.stem
        return self.finalize_result(
            file_path=file_path,
            relative_path=relative_path,
            tags=tags,
            document_title=document_title,
            text=text,
            sections=[],
            quality=quality,
            semantic_blocks=blocks,
            metadata={"extraction_method": "markdown_text"},
        )
