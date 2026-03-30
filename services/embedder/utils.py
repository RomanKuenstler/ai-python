from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path


def normalize_tags(tags: list[str] | tuple[str, ...], default_tag: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        cleaned = str(tag).strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(cleaned)
    return normalized or [default_tag]


def compute_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\u00a0", " ")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t\f\v]+$", "", normalized, flags=re.MULTILINE)
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


def save_tags(tags_path: Path, tags_map: dict[str, list[str]]) -> None:
    tags_path.parent.mkdir(parents=True, exist_ok=True)
    with tags_path.open("w", encoding="utf-8") as handle:
        json.dump(tags_map, handle, indent=2, sort_keys=True)
        handle.write("\n")
