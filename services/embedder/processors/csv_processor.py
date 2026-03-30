from __future__ import annotations

import csv

from services.embedder.processors.base_processor import BaseProcessor, ExtractionResult, SemanticBlock
from services.embedder.processors.extraction_quality import evaluate_text_quality
from services.embedder.processors.shared_normalization import normalize_block_text, normalize_inline_text


class CsvProcessor(BaseProcessor):
    processor_name = "csv"
    content_type = "text/csv"

    def process(self, *, file_path, relative_path: str, tags: list[str]) -> ExtractionResult:
        with file_path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)

        blocks: list[SemanticBlock] = []
        rendered_rows: list[str] = []
        if reader.fieldnames:
            for index, row in enumerate(rows, start=1):
                lines = [f"Row {index}:"]
                for field in reader.fieldnames:
                    value = normalize_inline_text(str(row.get(field, "")))
                    lines.append(f"{field}: {value}")
                rendered = "\n".join(lines)
                rendered_rows.append(rendered)
                blocks.append(
                    SemanticBlock(
                        text=rendered,
                        title=f"Row {index}",
                        section=f"Row {index}",
                        content_type=self.content_type,
                        metadata={"row_number": index},
                    )
                )

        text = normalize_block_text("\n\n".join(rendered_rows))
        quality = evaluate_text_quality(text)
        if not quality.is_useful:
            return ExtractionResult.empty(
                file_path=file_path,
                extension=file_path.suffix.lower(),
                content_type=self.content_type,
                tags=tags,
                quality=quality,
                reason="csv_extraction_not_useful",
                settings=self.settings,
            )

        return self.finalize_result(
            file_path=file_path,
            relative_path=relative_path,
            tags=tags,
            document_title=file_path.stem,
            text=text,
            sections=[{"title": block.title, "section": block.section} for block in blocks],
            quality=quality,
            semantic_blocks=blocks,
            metadata={"extraction_method": "csv_rows"},
        )
