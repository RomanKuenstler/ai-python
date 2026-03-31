from __future__ import annotations

from services.embedder.processors.extraction_quality import evaluate_text_quality


def test_quality_flags_broken_extraction() -> None:
    quality = evaluate_text_quality("� � � ||| ___ âââ")
    assert not quality.is_useful
    assert "broken_fragments" in quality.flags or "encoding_corruption" in quality.flags


def test_quality_accepts_realistic_text() -> None:
    quality = evaluate_text_quality(
        "Docker volumes persist application state across container restarts.\n\n"
        "Use bind mounts when you need direct access from the host."
    )
    assert quality.is_useful
