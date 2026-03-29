from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[^\S\n]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = "".join(ch for ch in normalized if ch.isprintable() or ch in "\n\t")
    return normalized.strip()


def load_tags(tags_path: Path) -> dict[str, list[str]]:
    if not tags_path.exists():
        return {}
    with tags_path.open("r", encoding="utf-8") as handle:
        content = json.load(handle)
    return {str(key): [str(tag) for tag in value] for key, value in content.items()}
