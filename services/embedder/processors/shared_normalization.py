from __future__ import annotations

import re

from services.embedder.utils import normalize_text


def normalize_block_text(text: str) -> str:
    lines = [line.rstrip() for line in normalize_text(text).split("\n")]
    cleaned: list[str] = []
    previous_blank = False
    for line in lines:
        blank = not line.strip()
        if blank and previous_blank:
            continue
        cleaned.append(line)
        previous_blank = blank
    return "\n".join(cleaned).strip()


def normalize_table_rows(rows: list[list[str]]) -> str:
    rendered = []
    for row in rows:
        cells = [normalize_inline_text(cell) for cell in row if normalize_inline_text(cell)]
        if cells:
            rendered.append(" | ".join(cells))
    return "\n".join(rendered).strip()


def normalize_inline_text(text: str) -> str:
    normalized = normalize_text(text)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def dedupe_consecutive_blocks(blocks: list[str]) -> list[str]:
    deduped: list[str] = []
    previous = None
    for block in blocks:
        if block == previous or not block.strip():
            previous = block
            continue
        deduped.append(block)
        previous = block
    return deduped
