from __future__ import annotations

from fastapi.testclient import TestClient

from services.retriever.api.app import create_app
from services.retriever.api.dependencies import get_retriever_service
from services.retriever.schemas.chat import (
    AttachmentRead,
    ChatDownloadResponse,
    ChatRead,
    LibraryFileRead,
    LibraryListResponse,
    LibrarySummaryRead,
    MessageRead,
    SettingsRead,
    SourceRead,
)


class StubRetrieverService:
    def create_chat(self) -> ChatRead:
        return ChatRead(
            id="chat-1",
            chat_name="chat-abc123",
            is_archived=False,
            created_at="2026-03-29T00:00:00Z",
            updated_at="2026-03-29T00:00:00Z",
        )

    def list_chats(self) -> list[ChatRead]:
        return [self.create_chat()]

    def get_chat(self, chat_id: str) -> ChatRead | None:
        if chat_id != "chat-1":
            return None
        return self.create_chat()

    def rename_chat(self, chat_id: str, chat_name: str) -> ChatRead | None:
        if chat_id != "chat-1":
            return None
        return ChatRead(
            id="chat-1",
            chat_name=chat_name,
            is_archived=False,
            created_at="2026-03-29T00:00:00Z",
            updated_at="2026-03-29T00:00:02Z",
        )

    def list_archived_chats(self) -> list[ChatRead]:
        return [
            ChatRead(
                id="chat-2",
                chat_name="archived-chat",
                is_archived=True,
                created_at="2026-03-29T00:00:00Z",
                updated_at="2026-03-29T00:00:03Z",
            )
        ]

    def archive_chat(self, chat_id: str) -> ChatRead | None:
        if chat_id != "chat-1":
            return None
        return ChatRead(
            id="chat-1",
            chat_name="chat-abc123",
            is_archived=True,
            created_at="2026-03-29T00:00:00Z",
            updated_at="2026-03-29T00:00:03Z",
        )

    def unarchive_chat(self, chat_id: str) -> ChatRead | None:
        if chat_id != "chat-2":
            return None
        return ChatRead(
            id="chat-2",
            chat_name="archived-chat",
            is_archived=False,
            created_at="2026-03-29T00:00:00Z",
            updated_at="2026-03-29T00:00:04Z",
        )

    def delete_chat(self, chat_id: str) -> ChatRead | None:
        if chat_id != "chat-1":
            return None
        return self.create_chat()

    def get_chat_messages(self, chat_id: str) -> list[MessageRead]:
        if chat_id != "chat-1":
            return []
        return [
            MessageRead(
                id="2",
                chat_id="chat-1",
                role="assistant",
                content="Grounded answer",
                status="completed",
                has_attachments=False,
                created_at="2026-03-29T00:00:01Z",
                sources=[
                    SourceRead(
                        chunk_id="chunk-1",
                        file_name="manual.pdf",
                        file_path="/app/data/manual.pdf",
                        title="Storage",
                        chapter="Chapter 4",
                        section="Volumes",
                        page_number=18,
                        score=0.812,
                        tags=["docker"],
                    )
                ],
                attachments=[],
            )
        ]

    def send_message(
        self,
        chat_id: str,
        user_content: str,
        attachments: list[tuple[str, bytes]] | None = None,
        assistant_mode: str | None = None,
    ):
        if chat_id != "chat-1":
            return None
        attachment_payload = [
            AttachmentRead(
                file_name="diagram.png",
                file_type="png",
                extraction_method="ocr",
                quality={"score": 0.91},
            )
        ]
        return {
            "chat_id": "chat-1",
            "user_message": MessageRead(
                id="1",
                chat_id="chat-1",
                role="user",
                content=user_content,
                status="completed",
                has_attachments=bool(attachments),
                created_at="2026-03-29T00:00:00Z",
                sources=[],
                attachments=attachment_payload if attachments else [],
            ),
            "assistant_message": MessageRead(
                id="2",
                chat_id="chat-1",
                role="assistant",
                content="Grounded answer",
                status="completed",
                has_attachments=False,
                created_at="2026-03-29T00:00:01Z",
                sources=[],
                attachments=[],
            ),
            "assistant_mode": assistant_mode or "simple",
            "sources": [
                SourceRead(
                    chunk_id="chunk-1",
                    file_name="manual.pdf",
                    file_path="/app/data/manual.pdf",
                    title="Storage",
                    chapter="Chapter 4",
                    section="Volumes",
                    page_number=18,
                    score=0.812,
                    tags=["docker"],
                )
            ],
            "attachments_used": attachment_payload if attachments else [],
        }

    def download_chat(self, chat_id: str) -> ChatDownloadResponse | None:
        if chat_id != "chat-1":
            return None
        return ChatDownloadResponse(
            chat_id="chat-1",
            chat_name="chat-abc123",
            is_archived=False,
            created_at="2026-03-29T00:00:00Z",
            updated_at="2026-03-29T00:00:01Z",
            messages=[
                {
                    "role": "user",
                    "content": "hello",
                    "created_at": "2026-03-29T00:00:00Z",
                    "sources": [],
                    "attachments": [],
                },
                {
                    "role": "assistant",
                    "content": "Grounded answer",
                    "created_at": "2026-03-29T00:00:01Z",
                    "sources": [
                        {
                            "chunk_id": "chunk-1",
                            "file_name": "manual.pdf",
                            "file_path": "/app/data/manual.pdf",
                            "title": "Storage",
                            "chapter": "Chapter 4",
                            "section": "Volumes",
                            "page_number": 18,
                            "score": 0.812,
                            "tags": ["docker"],
                        }
                    ],
                    "attachments": [],
                },
            ],
        )

    def get_settings(self) -> SettingsRead:
        return SettingsRead(
            chat_history_messages_count=5,
            max_similarities=8,
            min_similarities=2,
            similarity_score_threshold=0.7,
            default_assistant_mode="simple",
            available_assistant_modes=["simple", "refine"],
        )

    def update_settings(self, payload) -> SettingsRead:
        if payload.min_similarities > payload.max_similarities:
            raise ValueError("min similarities cannot be greater than max similarities")
        return SettingsRead(
            chat_history_messages_count=payload.chat_history_messages_count,
            max_similarities=payload.max_similarities,
            min_similarities=payload.min_similarities,
            similarity_score_threshold=payload.similarity_score_threshold,
            default_assistant_mode="simple",
            available_assistant_modes=["simple", "refine"],
        )

    def list_library_files(self) -> LibraryListResponse:
        return LibraryListResponse(
            files=[
                LibraryFileRead(
                    id=1,
                    file_name="manual.pdf",
                    file_path="/app/data/manual.pdf",
                    file_type="pdf",
                    extension=".pdf",
                    size_bytes=1024,
                    chunk_count=3,
                    tags=["docker"],
                    is_embedded=True,
                    is_enabled=True,
                    processing_status="processed",
                    updated_at="2026-03-29T00:00:00Z",
                )
            ],
            summary=LibrarySummaryRead(total_files=1, embedded_files=1, total_chunks=3),
            allowed_extensions=[".md", ".pdf"],
            max_upload_files=5,
            upload_max_file_size_mb=50,
            default_tag="default",
        )

    def upload_library_files(self, uploads, tags_by_file_raw: str | None):
        return {"files": self.list_library_files().files}

    def update_library_file(self, file_id: int, *, is_enabled: bool):
        if file_id != 1:
            return None
        record = self.list_library_files().files[0]
        return record.model_copy(update={"is_enabled": is_enabled})

    def delete_library_file(self, file_id: int):
        if file_id != 1:
            return None
        return self.list_library_files().files[0]


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_retriever_service] = lambda: StubRetrieverService()
    return TestClient(app)


def test_health_endpoint() -> None:
    client = build_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoints() -> None:
    client = build_client()
    response = client.post("/api/chats")
    assert response.status_code == 200
    assert response.json()["chat_name"].startswith("chat-")

    list_response = client.get("/api/chats")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    rename_response = client.patch("/api/chats/chat-1", json={"chat_name": "Renamed chat"})
    assert rename_response.status_code == 200
    assert rename_response.json()["chat_name"] == "Renamed chat"

    delete_response = client.delete("/api/chats/chat-1")
    assert delete_response.status_code == 200

    archived_response = client.get("/api/chats/archived")
    assert archived_response.status_code == 200
    assert archived_response.json()[0]["is_archived"] is True

    archive_response = client.patch("/api/chats/chat-1/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["is_archived"] is True

    unarchive_response = client.patch("/api/chats/chat-2/unarchive")
    assert unarchive_response.status_code == 200
    assert unarchive_response.json()["is_archived"] is False


def test_post_message_returns_sources() -> None:
    client = build_client()
    response = client.post("/api/chats/chat-1/messages", json={"message": "hello", "assistant_mode": "refine"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["assistant_message"]["content"] == "Grounded answer"
    assert payload["assistant_mode"] == "refine"
    assert payload["sources"][0]["file_name"] == "manual.pdf"
    assert payload["sources"][0]["section"] == "Volumes"


def test_post_message_supports_attachments() -> None:
    client = build_client()
    response = client.post(
        "/api/chats/chat-1/messages",
        data={"message": "Explain this image"},
        files={"files": ("diagram.png", b"fake-bytes", "image/png")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["user_message"]["has_attachments"] is True
    assert payload["attachments_used"][0]["file_name"] == "diagram.png"


def test_missing_chat_returns_404() -> None:
    client = build_client()
    response = client.get("/api/chats/missing")
    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}


def test_library_endpoints() -> None:
    client = build_client()

    list_response = client.get("/api/library/files")
    assert list_response.status_code == 200
    assert list_response.json()["files"][0]["extension"] == ".pdf"

    patch_response = client.patch("/api/library/files/1", json={"is_enabled": False})
    assert patch_response.status_code == 200
    assert patch_response.json()["is_enabled"] is False

    delete_response = client.delete("/api/library/files/1")
    assert delete_response.status_code == 200


def test_download_and_settings_endpoints() -> None:
    client = build_client()

    download_response = client.get("/api/chats/chat-1/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-disposition"].endswith('chat-abc123-chat-1.json"')
    assert download_response.json()["messages"][1]["sources"][0]["file_name"] == "manual.pdf"

    settings_response = client.get("/api/settings")
    assert settings_response.status_code == 200
    assert settings_response.json()["max_similarities"] == 8

    patch_response = client.patch(
        "/api/settings",
        json={
            "chat_history_messages_count": 6,
            "max_similarities": 9,
            "min_similarities": 3,
            "similarity_score_threshold": 0.75,
        },
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["similarity_score_threshold"] == 0.75
