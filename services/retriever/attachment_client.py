from __future__ import annotations

import base64

import httpx


class AttachmentProcessingClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def process_files(self, uploads: list[tuple[str, bytes]]) -> list[dict[str, object]]:
        payload = {
            "type": "attachment_processing",
            "files": [
                {
                    "file_name": file_name,
                    "content_base64": base64.b64encode(content).decode("ascii"),
                }
                for file_name, content in uploads
            ],
        }
        response = httpx.post(f"{self.base_url}/internal/process-attachments", json=payload, timeout=60.0)
        response.raise_for_status()
        return list(response.json().get("attachments", []))
