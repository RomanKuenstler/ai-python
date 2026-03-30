from __future__ import annotations

from services.common.models import ChatMessage, ChatSession, MessageAttachment, RetrievalLog
from services.common.models import SettingRecord
from services.retriever.postgres_client import RetrieverPostgresClient


class ChatRepository:
    def __init__(self, postgres_client: RetrieverPostgresClient) -> None:
        self.postgres_client = postgres_client

    def create_chat(self, chat_name: str) -> ChatSession:
        return self.postgres_client.create_chat(chat_name)

    def ensure_chat(self, chat_id: str, chat_name: str) -> ChatSession:
        return self.postgres_client.ensure_chat(chat_id, chat_name)

    def list_chats(self, *, archived: bool = False) -> list[ChatSession]:
        return self.postgres_client.list_chats(archived=archived)

    def get_chat(self, chat_id: str) -> ChatSession | None:
        return self.postgres_client.get_chat(chat_id)

    def rename_chat(self, chat_id: str, chat_name: str) -> ChatSession | None:
        return self.postgres_client.rename_chat(chat_id, chat_name)

    def delete_chat(self, chat_id: str) -> ChatSession | None:
        return self.postgres_client.delete_chat(chat_id)

    def set_chat_archived(self, chat_id: str, is_archived: bool) -> ChatSession | None:
        return self.postgres_client.set_chat_archived(chat_id, is_archived)

    def list_messages(self, chat_id: str) -> list[ChatMessage]:
        return self.postgres_client.get_chat_messages(chat_id)

    def create_message(
        self,
        chat_id: str,
        role: str,
        content: str,
        status: str = "completed",
        *,
        has_attachments: bool = False,
    ) -> ChatMessage:
        return self.postgres_client.add_chat_message(
            chat_id,
            role,
            content,
            status=status,
            has_attachments=has_attachments,
        )

    def add_message_attachments(self, message_id: int, attachments: list[dict[str, object]]) -> list[MessageAttachment]:
        return self.postgres_client.add_message_attachments(message_id, attachments)

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

    def get_attachments_by_message_ids(self, message_ids: list[int]) -> dict[int, list[MessageAttachment]]:
        return self.postgres_client.get_attachments_by_message_ids(message_ids)

    def touch_chat(self, chat_id: str) -> None:
        self.postgres_client.touch_chat(chat_id)

    def list_settings(self) -> list[SettingRecord]:
        return self.postgres_client.list_settings()

    def upsert_setting(self, key: str, value: str) -> SettingRecord:
        return self.postgres_client.upsert_setting(key, value)
