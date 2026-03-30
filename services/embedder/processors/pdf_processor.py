from __future__ import annotations

import logging
from collections import Counter

import fitz
import pypdfium2 as pdfium

from services.embedder.ocr import preprocess_image
from services.embedder.processors.base_processor import BaseProcessor, ExtractionResult, SemanticBlock
from services.embedder.processors.extraction_quality import evaluate_text_quality
from services.embedder.processors.shared_normalization import normalize_block_text

LOGGER = logging.getLogger(__name__)


class PdfProcessor(BaseProcessor):
    processor_name = "pdf"
    content_type = "pdf"

    def process(self, *, file_path, relative_path: str, tags: list[str]) -> ExtractionResult:
        direct_blocks = self._extract_direct(file_path)
        direct_text = "\n\n".join(block.text for block in direct_blocks if block.text.strip())
        direct_quality = evaluate_text_quality(
            direct_text,
            minimum_chars=self.settings.pdf_min_extracted_chars,
            minimum_avg_chars_per_page=self.settings.pdf_min_avg_chars_per_page,
            page_count=max(len(direct_blocks), 1),
        )

        use_ocr = False
        final_blocks = direct_blocks
        extraction_method = "text"
        quality = direct_quality

        if self.settings.pdf_ocr_mode == "ocr_only":
            use_ocr = self.settings.enable_ocr
        elif self.settings.pdf_ocr_mode == "fallback":
            use_ocr = self.settings.enable_ocr and not direct_quality.is_useful

        if use_ocr:
            LOGGER.warning(
                "Using OCR fallback",
                extra={"file_path": relative_path, "quality_flags": direct_quality.flags},
            )
            ocr_blocks = self._extract_ocr(file_path)
            ocr_text = "\n\n".join(block.text for block in ocr_blocks if block.text.strip())
            ocr_quality = evaluate_text_quality(
                ocr_text,
                minimum_chars=self.settings.pdf_min_extracted_chars,
                minimum_avg_chars_per_page=self.settings.pdf_min_avg_chars_per_page,
                page_count=max(len(ocr_blocks), 1),
            )
            if ocr_quality.is_useful and (not direct_quality.is_useful or len(ocr_text) >= len(direct_text)):
                final_blocks = ocr_blocks
                extraction_method = "ocr"
                quality = ocr_quality
            elif direct_quality.is_useful:
                extraction_method = "mixed"
                quality = direct_quality
            else:
                quality = ocr_quality

        final_text = "\n\n".join(block.text for block in final_blocks if block.text.strip())
        if not quality.is_useful or not final_text.strip():
            return ExtractionResult.empty(
                file_path=file_path,
                extension=file_path.suffix.lower(),
                content_type=self.content_type,
                tags=tags,
                quality=quality,
                reason="pdf_extraction_not_useful",
                settings=self.settings,
            )

        inferred_title = self._infer_title(final_blocks) or file_path.stem
        sections = [
            {"page_number": block.page_number, "section": block.section, "title": block.title}
            for block in final_blocks
        ]
        return self.finalize_result(
            file_path=file_path,
            relative_path=relative_path,
            tags=tags,
            document_title=inferred_title,
            text=final_text,
            sections=sections,
            quality=quality,
            semantic_blocks=final_blocks,
            metadata={"extraction_method": extraction_method},
            processing_flags={
                "processing_status": "processed",
                "processing_error": None,
                "ocr_used": extraction_method in {"ocr", "mixed"},
            },
        )

    def _extract_direct(self, file_path) -> list[SemanticBlock]:
        blocks: list[SemanticBlock] = []
        with fitz.open(file_path) as document:
            for index, page in enumerate(document, start=1):
                page_blocks = self._page_text_blocks(page)
                page_text = "\n".join(page_blocks).strip()
                if not page_text:
                    continue
                blocks.append(
                    SemanticBlock(
                        text=f"[Page {index}]\n{normalize_block_text(page_text)}",
                        title=f"Page {index}",
                        section=f"Page {index}",
                        page_number=index,
                        extraction_method="text",
                        content_type=self.content_type,
                        metadata={"page_number": index},
                    )
                )
        return blocks

    def _page_text_blocks(self, page: fitz.Page) -> list[str]:
        raw_blocks = page.get_text("blocks")
        if not raw_blocks:
            return []
        parsed = []
        for block in raw_blocks:
            x0, y0, x1, y1, text, *_ = block
            normalized = normalize_block_text(text)
            if normalized:
                parsed.append({"x0": x0, "y0": y0, "x1": x1, "text": normalized})
        if not parsed:
            return []
        if not self.settings.pdf_enable_column_detection:
            return [item["text"] for item in sorted(parsed, key=lambda item: (item["y0"], item["x0"]))]
        width = page.rect.width
        left = [item for item in parsed if item["x1"] <= width * 0.58]
        right = [item for item in parsed if item["x0"] >= width * 0.42]
        if len(left) >= 2 and len(right) >= 2:
            return [item["text"] for item in sorted(left, key=lambda item: (item["y0"], item["x0"]))] + [
                item["text"] for item in sorted(right, key=lambda item: (item["y0"], item["x0"]))
            ]
        return [item["text"] for item in sorted(parsed, key=lambda item: (item["y0"], item["x0"]))]

    def _extract_ocr(self, file_path) -> list[SemanticBlock]:
        blocks: list[SemanticBlock] = []
        pdf = pdfium.PdfDocument(str(file_path))
        for index in range(len(pdf)):
            page = pdf[index]
            bitmap = page.render(scale=self.settings.pdf_render_scale)
            pil_image = bitmap.to_pil()
            image = preprocess_image(pil_image, self.settings)
            import pytesseract

            text = normalize_block_text(pytesseract.image_to_string(image, lang=self.settings.ocr_language))
            if text:
                blocks.append(
                    SemanticBlock(
                        text=f"[Page {index + 1}]\n{text}",
                        title=f"Page {index + 1}",
                        section=f"Page {index + 1}",
                        page_number=index + 1,
                        extraction_method="ocr",
                        content_type=self.content_type,
                        metadata={"page_number": index + 1},
                    )
                )
        return blocks

    def _infer_title(self, blocks: list[SemanticBlock]) -> str | None:
        page_one = next((block for block in blocks if block.page_number == 1), None)
        if page_one:
            lines = [line.strip("# ").strip() for line in page_one.text.splitlines() if line.strip()]
            for line in lines:
                if len(line) > 8:
                    return line
        titles = [block.title for block in blocks if block.title]
        return Counter(titles).most_common(1)[0][0] if titles else None
