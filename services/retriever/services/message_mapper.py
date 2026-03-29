from __future__ import annotations

from services.common.models import ChatMessage, ChatSession, RetrievalLog
from services.retriever.schemas.chat import ChatRead, MessageRead, SourceRead


def map_chat(chat: ChatSession) -> ChatRead:
    return ChatRead(
        id=chat.id,
        chat_name=chat.chat_name,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
    )


def map_source(log: RetrievalLog) -> SourceRead:
    return SourceRead(
        chunk_id=log.chunk_id,
        file_name=log.source_file_name,
        file_path=log.source_file_path,
        title=log.chunk_title,
        chapter=log.chapter,
        section=log.section,
        page_number=log.page_number,
        score=log.retrieval_score,
        tags=list(log.tags or []),
    )


def map_message(message: ChatMessage, sources: list[RetrievalLog] | None = None) -> MessageRead:
    return MessageRead(
        id=str(message.id),
        chat_id=message.session_id,
        role=message.role,
        content=message.content,
        status=message.status,
        created_at=message.created_at,
        sources=[map_source(log) for log in (sources or [])],
    )
