from __future__ import annotations

from services.common.postgres import FileFilterState, TagFilterState
from services.common.models import ChatMessage, ChatSession, FileRecord, MessageAttachment, RetrievalLog
from services.retriever.schemas.chat import AttachmentRead, ChatRead, FilterFileRead, FilterTagRead, LibraryFileRead, MessageRead, SourceRead


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


def map_library_file(
    record: FileRecord,
    *,
    can_delete: bool = False,
    can_toggle_enabled: bool = True,
) -> LibraryFileRead:
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
        is_system=record.is_system,
        uploaded_by_user_id=record.uploaded_by_user_id,
        can_delete=can_delete,
        can_toggle_enabled=can_toggle_enabled,
        processing_status=record.processing_status,
        updated_at=record.updated_at,
    )


def map_filter_file(record: FileFilterState) -> FilterFileRead:
    return FilterFileRead(
        file_id=record.file_id,
        file_name=record.file_name,
        file_path=record.file_path,
        tags=list(record.tags),
        global_is_enabled=record.global_is_enabled,
        scoped_is_enabled=record.scoped_is_enabled,
        is_enabled=record.is_enabled,
        is_locked=record.is_locked,
        updated_at=record.updated_at,
    )


def map_filter_tag(record: TagFilterState) -> FilterTagRead:
    return FilterTagRead(
        tag=record.tag,
        file_count=record.file_count,
        global_is_enabled=record.global_is_enabled,
        scoped_is_enabled=record.scoped_is_enabled,
        is_enabled=record.is_enabled,
        is_locked=record.is_locked,
    )
