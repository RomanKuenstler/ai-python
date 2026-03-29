from __future__ import annotations

from services.common.postgres import PostgresClient


class ChatHistoryService:
    def __init__(self, postgres_client: PostgresClient, history_limit: int) -> None:
        self.postgres_client = postgres_client
        self.history_limit = history_limit

    def fetch(self, session_id: str) -> list[tuple[str, str]]:
        return [(message.role, message.content) for message in self.postgres_client.get_recent_chat_history(session_id, self.history_limit)]
