from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChatCreateResponse(BaseModel):
    id: str
    chat_name: str
    created_at: datetime
    updated_at: datetime


class ChatRead(ChatCreateResponse):
    pass


class ChatUpdateRequest(BaseModel):
    chat_name: str = Field(min_length=1)


class SourceRead(BaseModel):
    chunk_id: str
    file_name: str
    file_path: str
    title: str | None = None
    chapter: str | None = None
    section: str | None = None
    page_number: int | None = None
    score: float
    tags: list[str] = Field(default_factory=list)


class MessageRead(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    status: str
    has_attachments: bool = False
    created_at: datetime
    sources: list[SourceRead] = Field(default_factory=list)
    attachments: list["AttachmentRead"] = Field(default_factory=list)


class MessageCreateRequest(BaseModel):
    message: str = Field(min_length=1)


class AttachmentRead(BaseModel):
    file_name: str
    file_type: str
    extraction_method: str | None = None
    quality: dict = Field(default_factory=dict)


class MessageCreateResponse(BaseModel):
    chat_id: str
    user_message: MessageRead
    assistant_message: MessageRead
    sources: list[SourceRead] = Field(default_factory=list)
    attachments_used: list[AttachmentRead] = Field(default_factory=list)


class LibraryFileRead(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str
    extension: str
    size_bytes: int
    chunk_count: int
    tags: list[str] = Field(default_factory=list)
    is_embedded: bool
    is_enabled: bool
    processing_status: str
    updated_at: datetime


class LibrarySummaryRead(BaseModel):
    total_files: int
    embedded_files: int
    total_chunks: int


class LibraryListResponse(BaseModel):
    files: list[LibraryFileRead] = Field(default_factory=list)
    summary: LibrarySummaryRead
    allowed_extensions: list[str] = Field(default_factory=list)
    max_upload_files: int
    upload_max_file_size_mb: int
    default_tag: str


class LibraryFileUpdateRequest(BaseModel):
    is_enabled: bool | None = None


class LibraryUploadResponse(BaseModel):
    files: list[LibraryFileRead] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
