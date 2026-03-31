from __future__ import annotations

from services.common.postgres import PostgresClient


class ChatHistoryService:
    def __init__(self, postgres_client: PostgresClient, history_limit: int) -> None:
        self.postgres_client = postgres_client
        self.history_limit = history_limit

    def fetch(self, session_id: str, *, user_id: int, exclude_message_id: int | None = None) -> list[tuple[str, str]]:
        history = self.postgres_client.get_recent_chat_history(session_id, user_id=user_id, limit=self.history_limit)
        if exclude_message_id is not None:
            history = [message for message in history if message.id != exclude_message_id]
        return [(message.role, message.content) for message in history]
