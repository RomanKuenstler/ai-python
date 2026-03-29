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
    created_at: datetime
    sources: list[SourceRead] = Field(default_factory=list)


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1)


class MessageCreateResponse(BaseModel):
    chat_id: str
    user_message: MessageRead
    assistant_message: MessageRead
    sources: list[SourceRead] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
