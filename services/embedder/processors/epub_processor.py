from __future__ import annotations

import logging
import re
from collections import Counter

from ebooklib import ITEM_DOCUMENT, epub

from services.embedder.processors.base_processor import BaseProcessor, ExtractionResult, SemanticBlock
from services.embedder.processors.extraction_quality import evaluate_text_quality
from services.embedder.processors.html_processor import HtmlProcessor
from services.embedder.processors.shared_normalization import normalize_inline_text

LOGGER = logging.getLogger(__name__)

FRONT_MATTER_MARKERS = {
    "cover",
    "title page",
    "copyright",
    "table of contents",
    "contents",
    "front matter",
    "half title",
    "nav",
    "about the author",
    "about the reviewer",
    "preface",
    "acknowledgments",
    "acknowledgements",
    "dedication",
    "packt",
}

MAIN_CONTENT_PATTERN = re.compile(r"\b(chapter|part)\s+\d+\b", re.IGNORECASE)


class EpubProcessor(BaseProcessor):
    processor_name = "epub"
    content_type = "epub"

    def __init__(self, *, settings, data_dir):
        super().__init__(settings=settings, data_dir=data_dir)
        self.html_processor = HtmlProcessor(settings=settings, data_dir=data_dir)

    def process(self, *, file_path, relative_path: str, tags: list[str]) -> ExtractionResult:
        try:
            book = epub.read_epub(str(file_path))
        except Exception as exc:
            LOGGER.warning("Malformed EPUB package", extra={"file_path": relative_path, "error": str(exc)})
            return self._empty_result(file_path, tags, reason=f"epub_parse_error:{exc}")

        ordered_items = self._spine_items(book)
        blocks = self._extract_blocks(ordered_items, tags)
        if self.settings.epub_fallback_scan_enabled and not blocks:
            fallback_items = [item for item in book.get_items() if item.get_type() == ITEM_DOCUMENT]
            blocks = self._extract_blocks(fallback_items, tags)
        if self.settings.epub_remove_repeated_chrome:
            blocks = self._remove_repeated_chrome(blocks)

        text = "\n\n".join(block.text for block in blocks if block.text.strip())
        quality = evaluate_text_quality(text)
        if not quality.is_useful:
            return self._empty_result(file_path, tags, reason="epub_extraction_not_useful", quality=quality)

        title = self._first_metadata(book, "DC", "title") or file_path.stem
        author = self._first_metadata(book, "DC", "creator")
        return self.finalize_result(
            file_path=file_path,
            relative_path=relative_path,
            tags=tags,
            document_title=title,
            text=text,
            sections=[{"chapter": block.chapter, "section": block.section, "title": block.title} for block in blocks],
            quality=quality,
            semantic_blocks=blocks,
            metadata={"author": author, "extraction_method": "epub_spine"},
        )

    def _spine_items(self, book) -> list:
        items = []
        id_map = {item.get_id(): item for item in book.get_items()}
        for item_id, _ in book.spine:
            item = id_map.get(item_id)
            if item and item.get_type() == ITEM_DOCUMENT:
                items.append(item)
        return items

    def _extract_blocks(self, items: list, tags: list[str]) -> list[SemanticBlock]:
        blocks: list[SemanticBlock] = []
        started_main_content = False
        for index, item in enumerate(items, start=1):
            raw_html = item.get_body_content().decode("utf-8", errors="ignore")
            title, item_blocks = self.html_processor.extract_blocks(raw_html)
            label = normalize_inline_text(title or item.get_name() or item.get_id())
            if self.settings.epub_skip_front_matter and self._is_front_matter(
                label=label,
                item_name=item.get_name(),
                blocks=item_blocks,
                spine_index=index,
                started_main_content=started_main_content,
            ):
                continue
            if self._looks_like_main_content(label, item_blocks):
                started_main_content = True
            for block in item_blocks:
                block.chapter = block.chapter or label
                block.title = block.title or label
                block.content_type = self.content_type
                if not block.heading_path:
                    block.heading_path = [label]
                elif block.heading_path[0] != label:
                    block.heading_path = [label, *block.heading_path]
                block.section = block.section or (block.heading_path[-1] if block.heading_path else label)
                block.metadata["tags"] = tags
            if item_blocks:
                blocks.extend(item_blocks)
        return blocks

    def _remove_repeated_chrome(self, blocks: list[SemanticBlock]) -> list[SemanticBlock]:
        if not blocks:
            return blocks
        line_counts = Counter()
        per_block_lines: list[list[str]] = []
        for block in blocks:
            lines = [line.strip() for line in block.text.splitlines() if line.strip()]
            per_block_lines.append(lines)
            for line in set(lines):
                if len(line) < 120:
                    line_counts[line] += 1
        threshold = max(2, len(blocks) // 3)
        repeated = {line for line, count in line_counts.items() if count >= threshold}
        cleaned_blocks: list[SemanticBlock] = []
        for block, lines in zip(blocks, per_block_lines, strict=True):
            filtered = [line for line in lines if line not in repeated]
            if filtered:
                block.text = "\n".join(filtered)
                cleaned_blocks.append(block)
        return cleaned_blocks

    def _is_front_matter(
        self,
        *,
        label: str,
        item_name: str,
        blocks: list[SemanticBlock],
        spine_index: int,
        started_main_content: bool,
    ) -> bool:
        lowered = " ".join(
            [
                label.lower(),
                item_name.lower(),
                " ".join(block.text[:200].lower() for block in blocks[:3]),
            ]
        )
        if any(marker in lowered for marker in FRONT_MATTER_MARKERS):
            return True
        if started_main_content:
            return False
        if spine_index <= 12 and not self._looks_like_main_content(label, blocks):
            return True
        return False

    def _looks_like_main_content(self, label: str, blocks: list[SemanticBlock]) -> bool:
        if MAIN_CONTENT_PATTERN.search(label):
            return True
        for block in blocks[:5]:
            if MAIN_CONTENT_PATTERN.search(block.text) or MAIN_CONTENT_PATTERN.search(block.title or ""):
                return True
        return False

    def _first_metadata(self, book, namespace: str, name: str) -> str | None:
        values = book.get_metadata(namespace, name)
        if not values:
            return None
        return normalize_inline_text(str(values[0][0]))

    def _empty_result(self, file_path, tags: list[str], reason: str, quality=None) -> ExtractionResult:
        return ExtractionResult.empty(
            file_path=file_path,
            extension=file_path.suffix.lower(),
            content_type=self.content_type,
            tags=tags,
            quality=quality or evaluate_text_quality(""),
            reason=reason,
            settings=self.settings,
        )
