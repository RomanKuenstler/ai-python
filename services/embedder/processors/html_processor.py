from __future__ import annotations

from collections.abc import Iterable

from bs4 import BeautifulSoup, NavigableString, Tag

from services.embedder.processors.base_processor import BaseProcessor, ExtractionResult, SemanticBlock
from services.embedder.processors.extraction_quality import evaluate_text_quality
from services.embedder.processors.shared_normalization import (
    dedupe_consecutive_blocks,
    normalize_block_text,
    normalize_inline_text,
    normalize_table_rows,
)


REMOVABLE_TAGS = {
    "script",
    "style",
    "noscript",
    "svg",
    "canvas",
    "iframe",
    "nav",
    "footer",
    "aside",
    "form",
    "button",
    "input",
    "select",
    "textarea",
    "img",
    "picture",
    "video",
    "audio",
    "source",
    "meta",
    "link",
    "object",
    "embed",
}


class HtmlProcessor(BaseProcessor):
    processor_name = "html"
    content_type = "html"

    def process(self, *, file_path, relative_path: str, tags: list[str]) -> ExtractionResult:
        raw_html = file_path.read_text(encoding="utf-8", errors="ignore")
        title, semantic_blocks = self.extract_blocks(raw_html)
        normalized_blocks = [normalize_block_text(block.text) for block in semantic_blocks if block.text.strip()]
        filtered_blocks = dedupe_consecutive_blocks([block for block in normalized_blocks if self._is_meaningful(block)])
        final_blocks: list[SemanticBlock] = []
        index = 0
        for block in semantic_blocks:
            normalized = normalize_block_text(block.text)
            if index < len(filtered_blocks) and normalized == filtered_blocks[index]:
                block.text = normalized
                final_blocks.append(block)
                index += 1
        text = "\n\n".join(block.text for block in final_blocks if block.text.strip())
        quality = evaluate_text_quality(text)
        if not quality.is_useful:
            return ExtractionResult.empty(
                file_path=file_path,
                extension=file_path.suffix.lower(),
                content_type=self.content_type,
                tags=tags,
                quality=quality,
                reason="html_extraction_not_useful",
                settings=self.settings,
            )

        sections = [
            {
                "title": block.title,
                "section": block.section,
                "heading_path": block.heading_path,
            }
            for block in final_blocks
        ]
        return self.finalize_result(
            file_path=file_path,
            relative_path=relative_path,
            tags=tags,
            document_title=title,
            text=text,
            sections=sections,
            quality=quality,
            semantic_blocks=final_blocks,
            metadata={"extraction_method": "html_text"},
        )

    def extract_blocks(self, raw_html: str) -> tuple[str | None, list[SemanticBlock]]:
        soup = BeautifulSoup(raw_html, "html.parser")
        title = normalize_inline_text(soup.title.get_text(" ", strip=True)) if soup.title else None
        for element in soup.find_all(REMOVABLE_TAGS):
            element.decompose()

        root = (
            soup.find("main")
            or soup.find("article")
            or soup.find(attrs={"role": "main"})
            or soup.body
            or soup
        )
        heading_stack: list[tuple[int, str]] = []
        blocks: list[SemanticBlock] = []
        self._walk_children(root.children if isinstance(root, Tag) else [], blocks, heading_stack)
        if not title:
            for block in blocks:
                if block.title:
                    title = block.title
                    break
        return title, blocks

    def _walk_children(
        self,
        children: Iterable,
        blocks: list[SemanticBlock],
        heading_stack: list[tuple[int, str]],
    ) -> None:
        for child in children:
            if isinstance(child, NavigableString):
                continue
            if not isinstance(child, Tag) or self._is_hidden(child):
                continue
            name = child.name.lower()
            if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                level = int(name[1])
                heading = normalize_inline_text(child.get_text(" ", strip=True))
                if heading:
                    while heading_stack and heading_stack[-1][0] >= level:
                        heading_stack.pop()
                    heading_stack.append((level, heading))
                    blocks.append(
                        SemanticBlock(
                            text=f"{'#' * level} {heading}",
                            title=heading,
                            section=heading,
                            heading_path=[item[1] for item in heading_stack],
                            content_type=self.content_type,
                        )
                    )
                continue
            if name == "p":
                text = normalize_block_text(child.get_text(" ", strip=True))
                if text:
                    blocks.append(self._build_block(text, heading_stack))
                continue
            if name in {"ul", "ol"}:
                items = []
                for li in child.find_all("li", recursive=False):
                    item = normalize_inline_text(li.get_text(" ", strip=True))
                    if item:
                        items.append(f"- {item}")
                if items:
                    blocks.append(self._build_block("\n".join(items), heading_stack))
                continue
            if name == "blockquote":
                text = normalize_block_text(child.get_text("\n", strip=True))
                if text:
                    blocks.append(self._build_block("\n".join(f"> {line}" for line in text.splitlines()), heading_stack))
                continue
            if name in {"pre", "code"}:
                code = normalize_block_text(child.get_text("\n", strip=False))
                if code:
                    blocks.append(self._build_block(f"```\n{code}\n```", heading_stack))
                continue
            if name == "table":
                rows = []
                for row in child.find_all("tr"):
                    cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
                    if cells:
                        rows.append(cells)
                rendered = normalize_table_rows(rows)
                if rendered:
                    blocks.append(self._build_block(rendered, heading_stack))
                continue
            if name in {"main", "article", "section", "div", "body"}:
                self._walk_children(child.children, blocks, heading_stack.copy())
                continue
            text = normalize_block_text(child.get_text(" ", strip=True))
            if text and self._is_meaningful(text):
                blocks.append(self._build_block(text, heading_stack))

    def _build_block(self, text: str, heading_stack: list[tuple[int, str]]) -> SemanticBlock:
        heading_path = [heading for _, heading in heading_stack]
        section = heading_path[-1] if heading_path else None
        chapter = heading_path[0] if heading_path else None
        return SemanticBlock(
            text=text,
            title=section or chapter,
            chapter=chapter,
            section=section,
            heading_path=heading_path,
            content_type=self.content_type,
        )

    def _is_hidden(self, element: Tag) -> bool:
        if element.has_attr("hidden") or element.get("aria-hidden") == "true":
            return True
        style = (element.get("style") or "").replace(" ", "").lower()
        return "display:none" in style or "visibility:hidden" in style

    def _is_meaningful(self, text: str) -> bool:
        compact = normalize_inline_text(text)
        return len(compact) >= 3 and compact not in {"|", "-", ">", "#"}
