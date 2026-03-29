from __future__ import annotations

from fastapi.testclient import TestClient

from services.retriever.api.app import create_app
from services.retriever.api.dependencies import get_retriever_service
from services.retriever.schemas.chat import ChatRead, MessageRead, SourceRead


class StubRetrieverService:
    def create_chat(self) -> ChatRead:
        return ChatRead(
            id="chat-1",
            chat_name="chat-abc123",
            created_at="2026-03-29T00:00:00Z",
            updated_at="2026-03-29T00:00:00Z",
        )

    def list_chats(self) -> list[ChatRead]:
        return [self.create_chat()]

    def get_chat(self, chat_id: str) -> ChatRead | None:
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
            )
        ]

    def send_message(self, chat_id: str, user_content: str):
        if chat_id != "chat-1":
            return None
        return {
            "chat_id": "chat-1",
            "user_message": MessageRead(
                id="1",
                chat_id="chat-1",
                role="user",
                content=user_content,
                status="completed",
                created_at="2026-03-29T00:00:00Z",
                sources=[],
            ),
            "assistant_message": MessageRead(
                id="2",
                chat_id="chat-1",
                role="assistant",
                content="Grounded answer",
                status="completed",
                created_at="2026-03-29T00:00:01Z",
                sources=[],
            ),
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
        }


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


def test_post_message_returns_sources() -> None:
    client = build_client()
    response = client.post("/api/chats/chat-1/messages", json={"content": "hello"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["assistant_message"]["content"] == "Grounded answer"
    assert payload["sources"][0]["file_name"] == "manual.pdf"
    assert payload["sources"][0]["section"] == "Volumes"


def test_missing_chat_returns_404() -> None:
    client = build_client()
    response = client.get("/api/chats/missing")
    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}
