from __future__ import annotations

from services.retriever.source_formatter import format_sources


def test_source_formatter_includes_metadata() -> None:
    rendered = format_sources(
        [
            {
                "file_name": "manual.pdf",
                "title": "Storage Classes",
                "chapter": "Chapter 4",
                "section": "Volumes",
                "page_number": 18,
                "score": 0.81234,
                "tags": ["kubernetes"],
            }
        ]
    )
    assert "Used similarities: 1" in rendered
    assert "file=manual.pdf" in rendered
    assert "page=18" in rendered
    assert "score=0.81" in rendered


def test_source_formatter_handles_empty_results() -> None:
    assert "No sources were used." in format_sources([])
