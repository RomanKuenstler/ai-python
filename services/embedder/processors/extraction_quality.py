from __future__ import annotations

import re
import string

from services.embedder.processors.base_processor import ExtractionQuality


BROKEN_FRAGMENT_PATTERN = re.compile(r"(?:�|[\[\]{}<>|_=]{3,}|(?:\b\w\b\s*){10,})")


def evaluate_text_quality(
    text: str,
    *,
    minimum_chars: int = 120,
    minimum_avg_chars_per_page: int | None = None,
    page_count: int | None = None,
) -> ExtractionQuality:
    stripped = text.strip()
    char_count = len(stripped)
    printable_count = sum(1 for char in stripped if char in string.printable or char.isprintable())
    alphabetic_count = sum(1 for char in stripped if char.isalpha())
    words = re.findall(r"\b\w+\b", stripped)
    average_word_length = sum(len(word) for word in words) / len(words) if words else 0.0
    broken_fragments = BROKEN_FRAGMENT_PATTERN.findall(stripped)
    broken_fragment_ratio = len(broken_fragments) / max(len(words), 1)
    printable_ratio = printable_count / max(char_count, 1)
    alphabetic_ratio = alphabetic_count / max(char_count, 1)
    flags: list[str] = []

    if char_count == 0:
        flags.append("empty_extraction")
    if char_count and char_count < minimum_chars:
        flags.append("too_short")
    if printable_ratio < 0.85:
        flags.append("low_printable_ratio")
    if alphabetic_ratio < 0.20:
        flags.append("low_alphabetic_ratio")
    if average_word_length > 14 or (words and average_word_length < 2):
        flags.append("suspicious_word_length")
    if broken_fragment_ratio > 0.20:
        flags.append("broken_fragments")
    if "Ã" in stripped or "â" in stripped:
        flags.append("encoding_corruption")
    if minimum_avg_chars_per_page is not None and page_count:
        avg = char_count / max(page_count, 1)
        if avg < minimum_avg_chars_per_page:
            flags.append("low_avg_chars_per_page")

    is_useful = not flags or flags == ["too_short"]
    if "empty_extraction" in flags or "encoding_corruption" in flags or "broken_fragments" in flags:
        is_useful = False
    if minimum_avg_chars_per_page is not None and "low_avg_chars_per_page" in flags and char_count < minimum_chars:
        is_useful = False
    score = max(0.0, 1.0 - (len(flags) * 0.18))
    return ExtractionQuality(
        is_useful=is_useful,
        score=score,
        char_count=char_count,
        printable_ratio=printable_ratio,
        alphabetic_ratio=alphabetic_ratio,
        average_word_length=average_word_length,
        broken_fragment_ratio=broken_fragment_ratio,
        flags=flags,
    )
