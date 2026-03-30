from __future__ import annotations

from services.common.models import ChatMessage, ChatSession, FileRecord, MessageAttachment, RetrievalLog
from services.retriever.schemas.chat import AttachmentRead, ChatRead, LibraryFileRead, MessageRead, SourceRead


def map_chat(chat: ChatSession) -> ChatRead:
    return ChatRead(
        id=chat.id,
        chat_name=chat.chat_name,
        is_archived=chat.is_archived,
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


def map_attachment(attachment: MessageAttachment | dict[str, object]) -> AttachmentRead:
    if isinstance(attachment, MessageAttachment):
        return AttachmentRead(
            file_name=attachment.file_name,
            file_type=attachment.file_type,
            extraction_method=attachment.extraction_method,
            quality=dict(attachment.quality or {}),
        )
    return AttachmentRead(
        file_name=str(attachment["file_name"]),
        file_type=str(attachment["type"]),
        extraction_method=str(attachment.get("extraction_method") or "") or None,
        quality=dict(attachment.get("quality") or {}),
    )


def map_message(message: ChatMessage, sources: list[RetrievalLog] | None = None) -> MessageRead:
    return MessageRead(
        id=str(message.id),
        chat_id=message.session_id,
        role=message.role,
        content=message.content,
        status=message.status,
        has_attachments=message.has_attachments,
        created_at=message.created_at,
        sources=[map_source(log) for log in (sources or [])],
    )


def map_library_file(record: FileRecord) -> LibraryFileRead:
    return LibraryFileRead(
        id=record.id,
        file_name=record.file_name,
        file_path=record.file_path,
        file_type=record.file_type,
        extension=record.extension,
        size_bytes=record.size_bytes,
        chunk_count=record.chunk_count,
        tags=list(record.tags or []),
        is_embedded=record.is_embedded,
        is_enabled=record.is_enabled,
        processing_status=record.processing_status,
        updated_at=record.updated_at,
    )
