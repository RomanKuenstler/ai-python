from __future__ import annotations


def format_sources(retrieved_chunks: list[dict]) -> str:
    if not retrieved_chunks:
        return "--- Sources ---\nNo sources were used."

    lines = ["--- Sources ---", f"Used similarities: {len(retrieved_chunks)}"]
    for index, chunk in enumerate(retrieved_chunks, start=1):
        parts = [f"file={chunk.get('file_name', '')}"]
        title = chunk.get("title")
        chapter = chunk.get("chapter")
        section = chunk.get("section")
        page_number = chunk.get("page_number")
        score = chunk.get("score")
        tags = chunk.get("tags") or []
        if title:
            parts.append(f"title={title}")
        if chapter:
            parts.append(f"chapter={chapter}")
        if section and section != title:
            parts.append(f"section={section}")
        if page_number is not None:
            parts.append(f"page={page_number}")
        if score is not None:
            parts.append(f"score={float(score):.2f}")
        parts.append(f"tags={tags}")
        lines.append(f"[{index}] " + " | ".join(parts))
    return "\n".join(lines)
