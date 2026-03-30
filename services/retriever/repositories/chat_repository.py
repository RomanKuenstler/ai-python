from __future__ import annotations

from services.common.models import ChatMessage, ChatSession, RetrievalLog
from services.retriever.postgres_client import RetrieverPostgresClient


class ChatRepository:
    def __init__(self, postgres_client: RetrieverPostgresClient) -> None:
        self.postgres_client = postgres_client

    def create_chat(self, chat_name: str) -> ChatSession:
        return self.postgres_client.create_chat(chat_name)

    def ensure_chat(self, chat_id: str, chat_name: str) -> ChatSession:
        return self.postgres_client.ensure_chat(chat_id, chat_name)

    def list_chats(self) -> list[ChatSession]:
        return self.postgres_client.list_chats()

    def get_chat(self, chat_id: str) -> ChatSession | None:
        return self.postgres_client.get_chat(chat_id)

    def rename_chat(self, chat_id: str, chat_name: str) -> ChatSession | None:
        return self.postgres_client.rename_chat(chat_id, chat_name)

    def delete_chat(self, chat_id: str) -> ChatSession | None:
        return self.postgres_client.delete_chat(chat_id)

    def list_messages(self, chat_id: str) -> list[ChatMessage]:
        return self.postgres_client.get_chat_messages(chat_id)

    def create_message(self, chat_id: str, role: str, content: str, status: str = "completed") -> ChatMessage:
        return self.postgres_client.add_chat_message(chat_id, role, content, status=status)

    def create_retrieval_logs(
        self,
        *,
        assistant_message_id: int,
        user_message_id: int,
        chat_id: str,
        used_chunks: list[dict[str, str | float | list[str] | None]],
    ) -> None:
        self.postgres_client.add_retrieval_logs(
            assistant_message_id=assistant_message_id,
            user_message_id=user_message_id,
            session_id=chat_id,
            used_chunks=used_chunks,
        )

    def get_recent_history(self, chat_id: str, limit: int) -> list[ChatMessage]:
        return self.postgres_client.get_recent_chat_history(chat_id, limit)

    def get_sources_by_assistant_message(self, assistant_message_ids: list[int]) -> dict[int, list[RetrievalLog]]:
        return self.postgres_client.get_retrieval_logs_for_assistant_messages(assistant_message_ids)

    def touch_chat(self, chat_id: str) -> None:
        self.postgres_client.touch_chat(chat_id)
